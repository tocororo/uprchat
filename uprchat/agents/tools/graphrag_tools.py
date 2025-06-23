
import json
from typing import Annotated, Dict, List
from neo4j import EagerResult, GraphDatabase
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool, InjectedToolCallId
from langgraph.types import Command
import numpy as np
import openai
from pydantic import BaseModel, Field

from uprchat.app.config import get_settings
from uprchat.harvester.logger import setup_logger
from uprchat.mapper.services import RepositoryService
from uprchat.mapper.vectors.strategies.sentence_transformer import TransformerVectorizer
from uprchat.utils.apikey_iterator import APIKeyIterator

settings = get_settings()

logger = setup_logger("agent_tools")

apikey_iterator = APIKeyIterator()

vectorizer = TransformerVectorizer()

class GraphQueryInput(BaseModel):
    query: str = Field(..., description="Natural language question to search in the knowledge graph.")

class ContextOutput(BaseModel):
    context: List[Dict] 
    sources: List[str] = Field(
        default_factory=list, description="List of sources used to generate the context."
    )

@tool
def get_context_from_graph( 
    input: str,
    tool_call_id: Annotated[str, InjectedToolCallId]
) -> Command:
    """
    Retrieve information related to the given query by consulting the knowledge graph. This step is particularly recommended when there is limited context available or when the subject matter of the user's query is not clearly understood. The retrieved information can be used to answer the user's question or to provide relevant context for subsequent processing.
    """
    try:
        query = input
        cypher_query = generate_cypher_query(query)
        data_by_cypher = get_data_by_cypher_query(cypher_query)
        data_by_vectors = execute_vectorial_query(query)
        data = merge_unique_by_id(data_by_cypher, data_by_vectors)
        sources = []
        if not data:
            data = []
        else:
            sources = extract_sources(data)
        return Command(
            update={
                "sources": sources,
                "messages": [
                    ToolMessage(
                        content=f"Information retrieved from the knowledge graph for query '{query}': {json.dumps(data, indent=2)}",
                        tool_call_id=tool_call_id
                    )
                ]
            }
        )
    except Exception as e:
        logger.error(f"Error in get_context_from_graph for query='{query}': {e}")
        return Command(
            update={
                "sources": [],
                "messages": [
                    ToolMessage(
                        content="No was possible to retrieve information from the knowledge graph.",
                        tool_call_id=tool_call_id
                    )
                ]
            }
        )

def extract_sources(data: List[Dict]) -> List[str]:
    """
    Extracts source information from the provided data.
    Assumes that each dictionary in the list has a 'source' key.
    """
    sources = []
    for item in data:
        if isinstance(item, dict) and item.get('id', None):
            source = item['id']
            if isinstance(source, str) and source not in sources and source.startswith("http"):
                sources.append(source)
    return sources

def merge_unique_by_id(json_str1, json_str2):
    try:
        list1 = json.loads(json_str1)
        list2 = json.loads(json_str2)
    except json.JSONDecodeError as e:
        raise ValueError(f"Error al parsear las cadenas JSON: {e}")

    seen_ids = set()
    merged_list = []

    for obj in list1 + list2:
        obj_id = obj.get("id")
        if obj_id is not None and obj_id not in seen_ids:
            seen_ids.add(obj_id)
            merged_list.append(obj)

    return merged_list

def eager_result_to_json_string(result: EagerResult) -> str:
    if not result or not result.records:
        return json.dumps([])
    rows = []
    for record in result.records:
        for key in record.keys():
            node = record.get(key)
            if not node or not hasattr(node, '_properties'):
                continue
            row = {p: node._properties[p] for p in node._properties.keys() if p != "vectors"}
            rows.append(row)
    return json.dumps(rows, indent=2, default=str)

def vectorize_query(query: str):
    vector = vectorizer.vectorize(query)
    return vector

def get_data_by_cypher_query(query: str):
    r_service: RepositoryService = RepositoryService()
    result = r_service.execute_external_query(query)
    return eager_result_to_json_string(result)

def execute_vectorial_query(query: str)->str:
    vectors = vectorize_query(query)
    list_vectors = np.array(vectors).tolist()
    list_vectors = "[" + ", ".join(f"{x:.8f}" for x in list_vectors) + "]"
    query = f"""
    MATCH (n)
    WHERE n.vectors IS NOT NULL
    WITH {list_vectors} AS queryEmbedding, n
    WITH n,
        reduce(s = 0.0, i IN range(0, size(queryEmbedding)-1) | s + queryEmbedding[i] * n.vectors[i]) AS dot,
        reduce(s = 0.0, i IN range(0, size(queryEmbedding)-1) | s + queryEmbedding[i]^2) AS queryNormSq,
        reduce(s = 0.0, i IN range(0, size(n.vectors)-1) | s + n.vectors[i]^2) AS nodeNormSq
    WITH n, dot / (sqrt(queryNormSq) * sqrt(nodeNormSq)) AS cosineSimilarity
    RETURN n
    ORDER BY cosineSimilarity DESC
    LIMIT 5
    """
    result = get_data_by_cypher_query(query)
    return result

def generate_cypher_query(query: str) -> str:
    """
    Uses an LLM to translate a natural language question into a Cypher query,
    given the current database schema extracted via get_nodes_schema().
    """
    llm = apikey_iterator.get_llm()

    schema = get_nodes_schema()

    system_prompt = f"""
        You are an expert in Neo4j Cypher. Given the database schema and a user's question,
        generate exactly the Cypher query that answers the question.
        Schema:
        {schema}
        Requirements:
        - Output must be only the Cypher query in plain text.
        - Do NOT include any headers, code fences, markdown formatting, or extra commentary.
        - The query must be valid Cypher syntax.
        - The query always returns nodes and relationships, not just properties.
    """
    try:
        response = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=query)])
        return response.content
    except openai.RateLimitError as e:
        logger.error(e)
        apikey_iterator.change_apikey()
        llm = apikey_iterator.get_llm()
        return generate_cypher_query(query)

def get_nodes_schema() -> str:
    """
    Connects to a Neo4j database using the native driver and extracts a textual schema,
    including node labels with their properties and relationship types.
    Returns:
        str: Formatted schema as a string
    """
    schema_lines = []

    driver = GraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_user, settings.neo4j_pass)
    )

    node_query = "CALL db.schema.nodeTypeProperties()"
    result_nodes = driver.execute_query(node_query)
    node_props = {}

    for record in result_nodes.records:
        label = record["nodeType"]
        prop = record["propertyName"]
        # NOTE: Neo4j warns that `propertyTypes` output format may change in future versions.
        prop_type = record["propertyTypes"][0] if record["propertyTypes"] else "UNKNOWN"
        if label not in node_props:
            node_props[label] = []
        node_props[label].append(f"{prop}: {prop_type}")

    for label, props in node_props.items():
        props_str = ", ".join(props)
        schema_lines.append(f"(:{label} {{{props_str}}})")

    rel_query = "CALL db.schema.visualization()"
    result_rels = driver.execute_query(rel_query)

    rels_data = None
    if result_rels.records:
        record = result_rels.records[0]
        if len(record.keys()) == 1:
            rels_data = list(record.values())[0]
        else:
            rels_data = record.get("relationships", [])

    if rels_data:
        for rel in rels_data:
            start_labels, end_labels = rel.nodes
            rel_type = rel.type

            start = start_labels._properties["name"] if start_labels else "Unknown"
            end = end_labels._properties["name"] if end_labels else "Unknown"

            schema_lines.append(f"(:{start})-[:{rel_type}]->(:{end})")

    driver.close()
    return "\n".join(schema_lines)
