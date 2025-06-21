
from typing import  TypedDict, Sequence, Annotated
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, ToolMessage, SystemMessage, HumanMessage, AIMessage
from langgraph.prebuilt import ToolNode
import openai

from uprchat.agents.tools.graphrag_tools import  get_context_from_graph
from uprchat.app.config import get_settings
from uprchat.harvester.logger import setup_logger
from uprchat.utils.apikey_iterator import APIKeyIterator

logger = setup_logger("agent")

settings = get_settings()
apikey_iterator = APIKeyIterator()

MAINMODEL = settings.mainmodel
MODEL_API_KEY = apikey_iterator.get_current_apikey()
BASE_URL = settings.base_url

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    username: str
    user_type: str


llm = apikey_iterator.get_llm()

tools = [get_context_from_graph]

llm.bind_tools(tools=tools)

def generate_response(state: AgentState) -> AgentState:
    """
    Generates a response based on the context retrieved from the graph database.
    """
    messages = state["messages"]
    try:
        global llm
        response = llm.invoke([
            SystemMessage(content="You are a helpful assistant that provides information based on the context provided.")
        ] + messages)
    except openai.RateLimitError as e:
        logger.error(e)
        apikey_iterator.change_apikey()
        llm = apikey_iterator.get_llm()
        return generate_response(state)
    
    messages.append(AIMessage(content=response.content))
    
    return {"messages": messages}

def consult_kgraph(state: AgentState) -> AgentState:
    """
    Consults the knowledge graph to retrieve context based on the user's query.
    """
    messages = state["messages"]
    last_message = messages[-1]

    if isinstance(last_message, HumanMessage):
        query = last_message.content
        context = get_context_from_graph.invoke(query)
        messages.append(ToolMessage(content=context, tool_call_id="consult_kgraph"))
    
    return {"messages": messages}

def should_continue(state: AgentState):
    messages = state["messages"]
    last = messages[-1]
    if not last.tool_calls: 
        return "end"
    else:
        return "continue"

graph = StateGraph(AgentState)

graph.add_node(
    "consult_kgraph",
    consult_kgraph
)

graph.add_node("generate_response", generate_response)
graph.add_node(
    "tools",
    ToolNode(tools=tools)
)

graph.set_entry_point("consult_kgraph")
graph.add_edge("consult_kgraph", "generate_response")

graph.add_conditional_edges(
    "generate_response",
    should_continue,
    {
        "continue": "tools",
        "end": END
    }
)

agent = graph.compile()
