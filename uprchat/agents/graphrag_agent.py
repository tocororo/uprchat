
from typing import  TypedDict, Sequence, Annotated
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, SystemMessage, AIMessage
from langgraph.prebuilt import ToolNode
import openai
from langgraph.checkpoint.memory import MemorySaver

from uprchat.agents.tools.graphrag_tools import  get_context_from_graph
from uprchat.app.config import get_settings
from uprchat.harvester.logger import setup_logger
from uprchat.utils.apikey_iterator import APIKeyIterator

logger = setup_logger("agent")

settings = get_settings()
apikey_iterator = APIKeyIterator()
memory = MemorySaver()

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    username: str
    user_type: str

def system_prompt():
    return SystemMessage(content="""You are a helpful assistant, UPR-Assistant, that provides information based on the context provided. You must respond strictly based on that context when it is available and clearly related to the query. If the context is ambiguous, unrelated, or absent, you must respond using the information you have access to. Do not mention that you were given or not given context under any circumstance.""")

tools = [get_context_from_graph]

def setup_model():
    model = apikey_iterator.get_llm()
    model = model.bind_tools(tools=tools)
    return model

llm = setup_model()

def generate_response(state: AgentState) -> AgentState:
    """
    Generates a response based on the context retrieved from the graph database.
    """
    messages = state["messages"]
    try:
        global llm
        response = llm.invoke([
            system_prompt()
        ] + messages)
    except openai.RateLimitError as e:
        logger.error(e)
        apikey_iterator.change_apikey()
        setup_model()
        return generate_response(state)
    
    if hasattr(response, "tool_calls") and response.tool_calls:
        return {"messages": messages + [response]}
    else:
        return {"messages": messages + [AIMessage(content=response.content)]}

def should_continue(state: AgentState) -> str:
    """
    Determines whether to continue by invoking a tool or to end the workflow.

    Returns:
        - "continue": if the last message contains tool_calls.
        - END: if there are no tools to be executed.
    """
    messages = state["messages"]
    last_message = messages[-1]
    if isinstance(last_message, AIMessage):
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "continue"
    return "end"


graph = StateGraph(AgentState)

graph.add_node("generate_response", generate_response)
graph.add_node(
    "tools",
    ToolNode(tools=tools)
)

graph.set_entry_point("generate_response")

graph.add_conditional_edges(
    "generate_response",
    should_continue,
    {
        "continue": "tools",
        "end": END
    }
)

graph.add_edge("tools", "generate_response")

agent = graph.compile(checkpointer=memory)

def get_graph_image(output_path: str):
    dot = agent.get_graph().draw_mermaid_png()

    with open(output_path, "wb") as f:
        f.write(dot)

    logger.info(f"Graph saved in: {output_path.resolve()}")
