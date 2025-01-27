from typing import List
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from neo4j import GraphDatabase


class SimpleAgent:

    def __init__(
        self,
        model: str,
        model_txt2cypher: str,
        neo_uri: str,
        user: str,
        password: str,
        prop_descriptions: str,
    ):
        llm = ChatOllama(model=model)
        txt2cypher_llm = ChatOllama(model=model_txt2cypher)
        self.__neo_driver = GraphDatabase.driver(neo_uri, auth=(user, password))
        self.__prop_descriptions = prop_descriptions
        prompt_txt2query = ChatPromptTemplate(
            [
                (
                    "system",
                    """
                    ## Task:

                    Generate Cypher queries to query a Neo4j graph database based on the provided schema definition.

                    ## Instructions:

                    You are an expert at generating Cypher queries to query a Neo4j graph database based on the provided schema definition.
                    Use only the provided relationship types and properties.
                    Do not use any other relationship types or properties that are not provided.
                    If you cannot generate a Cypher statement based on the provided schema, explain the reason to the user.
                    Try to eliminate duplicate results.

                    ## Schema:

                    {node_schema}
                    {rel_schema}

                    Note: Do not include any explanations or apologies in your responses.
                    Reply with the Cypher query only, nothing more, in plain text, no line breaks""".strip(),
                ),
                ("user", "{query}"),
            ]
        )
        parser = StrOutputParser()
        self.__agent_txt2query = prompt_txt2query | txt2cypher_llm | parser
        generation_system_instruction = """
                    You are a movies expert, and your goal is to answer the user's question.
                    You will be provided with a table of results from a graph database query.
                    The results are related to the user's question and may represent appereances,
                    counts, or relationships between entities.
                    Do not mention that the results are coming from a neo4j database.
                    Your task is to generate a response to the user's question based on the provided results.
                    Do not use any information that is not provided in the results.  
                    If the results are empty, explain it to the user. 
                    Use all the information provided to you to answer the question.
                    Be as comprehensive as possible. 
                    """.strip()
        generation_prompt = """These are the results from a graph database query related to the user's question:

            {results_table}

            And the user's question you must answer using the results"""
        prompt = ChatPromptTemplate(
            [
                ("system", generation_system_instruction),
                ("system", generation_prompt),
                ("user", "{query}"),
            ]
        )
        self.__agent = prompt | llm | parser

    def __query_database(self, neo_query: str):
        with self.__neo_driver.session() as session:
            result = session.run(neo_query)
            output = [r.values() for r in result]
            output.insert(0, result.keys())
            return output

    def __get_nodes_schema(self):

        node_properties_query = """CALL apoc.meta.data()
                YIELD label, other, elementType, type, property
                WHERE NOT type = "RELATIONSHIP" AND elementType = "node"
                WITH label AS nodeLabels, collect(property) AS properties
                RETURN {labels: nodeLabels, properties: properties} AS output
                """

        node_props = self.__query_database(node_properties_query)
        nodes = [node[0] for node in node_props[1:]]

        node_descriptions = []
        for node in nodes:
            listable_properties = sorted(
                [
                    prop
                    for prop in node["properties"]
                    if prop in self.__prop_descriptions
                ]
            )
            node_description = f" - {node['labels']}, with properties: {', '.join(listable_properties)}"
            node_descriptions.append(node_description)

        prop_descriptions = [
            f" - {prop}: {self.__prop_descriptions[prop]}"
            for prop in sorted(self.__prop_descriptions)
        ]

        property_description_instructions = [
            "### Nodes",
            "",
            "The following are the nodes in the graph database, along with their properties.",
            "The property descriptions are listed at the end.",
            "",
            *node_descriptions,
            "",
            "Property descriptions:",
            *prop_descriptions,
        ]

        return "\n".join(property_description_instructions)

    def __get_rel_schema(self):

        rel_query = """
                CALL apoc.meta.data()
                YIELD label, other, elementType, type, property
                WHERE type = "RELATIONSHIP" AND elementType = "node"
                RETURN {source: label, relationship: property, target: other} AS output
                """

        rels = self.__query_database(rel_query)
        rels = [r[0] for r in rels[1:]]

        rel_descriptions = []
        for rel in rels:
            targets = ", ".join([f"`{t}`" for t in rel["target"]])
            rel_description = f" - `{rel['relationship']}`, that relates `{rel['source']}` with {targets}"
            rel_descriptions.append(rel_description)

        rel_props_descriptions = {
            "relation": "When used as a property of `related_to`, it specifies the type of relationship between two entities"
        }

        rel_props_descriptions = [
            f" - {prop}: {rel_props_descriptions[prop]}"
            for prop in sorted(rel_props_descriptions)
        ]

        rels_description_instructions = [
            "### Relationships",
            "",
            "The following are the relationships in the graph database",
            "",
            *rel_descriptions,
            "",
            "Property descriptions:",
            *rel_props_descriptions,
        ]

        return "\n".join(rels_description_instructions)

    def __execute_cypher_query(self, question: str):

        node_schema = self.__get_nodes_schema()
        rel_schema = self.__get_rel_schema()

        query = self.__agent_txt2query.invoke(
            {"node_schema": node_schema, "rel_schema": rel_schema, "query": question}
        )
        context = ""
        try:
            context = self.__query_database(query)
        except Exception:
            context = self.__execute_cypher_query(question)
        return context

    def __format_results_as_table(self, results: List[str]):
        if not results:
            return ""

        headers = results[0]

        columns = len(headers)

        column_widths = [len(header) for header in headers]

        for result in results[1:]:
            column_widths = [
                max(column_width, len(value))
                for column_width, value in zip(column_widths, result)
            ]

        rows = []

        def format_row(row, space_char=" "):
            return (
                "|"
                + (
                    "|".join(
                        [
                            f"{space_char}{value:<{column_widths[i]}}{space_char}"
                            for i, value in enumerate(row)
                        ]
                    )
                )
                + "|"
            )

        rows.append(format_row(headers))
        rows.append(format_row(["-" * column_widths[i] for i in range(columns)], "-"))
        for result in results[1:]:
            rows.append(format_row(result))
        rows.append("")
        return "\n".join(rows)

    def __retriever_information(self, question: str) -> str:
        results = self.__execute_cypher_query(question)
        results_table = self.__format_results_as_table(results)
        return results_table

    def generate_response(self, question: str) -> str:
        results_table = self.__retriever_information(question)
        return self.__agent.invoke({"results_table": results_table, "query": question})
