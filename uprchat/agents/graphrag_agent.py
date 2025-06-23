
import asyncio
from typing import  Optional, TypedDict, Sequence, Annotated
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, SystemMessage, AIMessage, HumanMessage, ToolMessage
from langgraph.prebuilt import ToolNode
from langgraph.types import Command
from langchain_core.tools import InjectedToolCallId, tool
import openai
from psycopg_pool import AsyncConnectionPool
from psycopg.rows import dict_row
from uprchat.agents.memory import DB_URI
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from uprchat.agents.tools.graphrag_tools import  get_context_from_graph
from uprchat.app.config import get_settings
from uprchat.harvester.logger import setup_logger
from uprchat.utils.apikey_iterator import APIKeyIterator

logger = setup_logger("agent")

settings = get_settings()
apikey_iterator = APIKeyIterator()

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    username: str
    user_type: str
    form_json: Optional[str]
    sources: Optional[Sequence[str]]

def system_prompt():
    return SystemMessage(content="""You are a helpful assistant, UPR-Assistant, that provides information based on the context provided. You must respond strictly based on that context when it is available and clearly related to the query. If the context is ambiguous, unrelated, or absent, you must respond using the information you have access to. Do not mention that you were given or not given context under any circumstance.""")

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
        llm = setup_model()
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
@tool
def generate_form_json(
    input_text: str,
    tool_call_id: Annotated[str, InjectedToolCallId]
) -> Command:
    """
    Generate a JSON that represents a dynamic form through which the information provided in the input will be requested from the user.
    """
    prompt= SystemMessage(content="""
    You are a generator of forms in JSON format. Your task is to interpret a **text string that describes what information the user should be asked for**, and based on that, generate a JSON object that represents a dynamic form.

    ### Rules:

    1. Your output must be **only a valid JSON object**, with no code blocks, no additional text, and no explanations. **Only the raw JSON**.

    2. The generated JSON must have the following structure:

    - `"formAttributes"`: An object with standard HTML `<form>` attributes, such as:
    - `"id"`: A unique identifier for the form.
    - `"class"`: Optional CSS class name.
    - You may include custom attributes (e.g., `data-*`) if useful for validation or behavior.

    - `"fields"`: An array of objects, each representing a form field.  
    Each field object must include at least:
    - `"type"`: One of `"text"`, `"email"`, `"password"`, `"select"`, `"radio"`, `"checkbox"`, or `"textarea"`.
    - `"name"`: The name/key under which the field value will be submitted.
    - `"label"`: A user-facing label for the field.
    - `"required"` *(optional)*: A boolean indicating whether the field is mandatory.
    - `"placeholder"` *(optional)*: A suggestion or helper text shown inside the input field.

    If the field is of type `"select"`, `"radio"`, or a `"checkbox"` with multiple choices, include:
    - `"options"`: An array of objects of the form `{ "value": "...", "label": "..." }`.

    If it's a single checkbox (e.g., for terms acceptance), `"options"` is not required.

    3. Intelligently interpret the given textual instruction. For example:

    - If you receive: `"Authentication form"` → generate fields for username and password.
    - If you receive: `"Customer contact information"` → include name, email, and phone fields.
    - If you receive: `"Satisfaction survey form"` → include rating options, comments, etc.

    4. Use clear, consistent, and semantically appropriate `label`, `name`, and `placeholder` values according to the context of the instruction.

    5. Field identifiers (`id`, `name`) should be valid, lowercase, and use no spaces or special characters.

    Reminder: **Your output must be a plain JSON object representing the form, without code blocks or any additional explanations.**

    *Example input you might receive:*

    > "Job application form"

    In that case, you should generate fields like full name, email, work experience, etc., following the rules above.
    """)
    response = apikey_iterator.get_llm().invoke([prompt, HumanMessage(content=input_text)])
    
    return Command(update={
        "form_json": response.content,
        "messages": [
            ToolMessage(
                content="Form JSON generated successfully.",
                tool_call_id=tool_call_id
            )
        ]
    })

tools = [get_context_from_graph, generate_form_json]

def setup_model():
    model = apikey_iterator.get_llm()
    model = model.bind_tools(tools=tools)
    return model

llm = setup_model()

def build_graph():
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
    return graph

async def main():
    async with AsyncConnectionPool(
        conninfo=DB_URI, 
        kwargs={
            "autocommit": True, 
            "prepare_threshold": 0, 
            "row_factory": dict_row
            }
        ) as pool, pool.connection() as conn:
        
        memory = AsyncPostgresSaver(conn)
        graph = build_graph()
        agent = graph.compile(checkpointer=memory)
        user = input("Usuario: ")
        question = input("Pregunta: ")
        while input != "exit":
            response = await agent.ainvoke(
                {
                    "messages": [
                        HumanMessage(content=question),
                    ],
                    "username": "test_user",
                    "user_type": "test"
                },
                config={"configurable": {"thread_id": user}}
            )
            print(response["messages"])
            print(response["messages"][-1].content)
            
            question = input("Pregunta: ")

def get_graph_image(agent, output_path: str):
    dot = agent.get_graph().draw_mermaid_png()

    with open(output_path, "wb") as f:
        f.write(dot)

    logger.info(f"Graph saved in: {output_path}")

def testing_agent():
    asyncio.run(main())
