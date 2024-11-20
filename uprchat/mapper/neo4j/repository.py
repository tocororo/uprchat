from neo4j import GraphDatabase
from uprchat.mapper.types.mapper_types import Node


class Neo4jRepository:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def _process_node_properties(self, properties: dict):
        if not bool(properties):
            return

        property_string: str = " {"
        for index, key in enumerate(properties):
            if isinstance(properties[key], int) or isinstance(properties[key], list):
                property_string += f"`{key}`: {properties[key]} "
            else:
                property_string += f"`{key}`: '{properties[key]}' "
            if index != len(properties) - 1:
                property_string += ", "
        property_string += "}"
        return property_string

    def add_node(self, node: Node):
        if node.properties is not None:
            query: str = (
                f"MERGE (:{node.label} {self._process_node_properties(node.properties)})"
            )
        else:
            query: str = f"MERGE(:{node.label})"
        return self.driver.execute_query(
            query,
            database_="neo4j",
        )

    def add_relation(
        self,
        start_id: str,
        start_label: str,
        end_id: str,
        end_label: str,
        relation_label: str,
    ):

        query: str = (
            f"MATCH (a:{start_label} {{id: '{start_id}'}}), (b:{end_label} {{id: '{end_id}'}})"
            f"MERGE (a)-[r:{relation_label}]->(b)"
        )
        print("the query", query)
        return self.driver.execute_query(query, database_="neo4j")

    def drop_graph(self):
        self.driver.execute_query(
            "MATCH (a) -[r] -> () DELETE a, r ", database_="neo4j"
        )
        self.driver.execute_query("MATCH (a) DELETE a", database_="neo4j")

    def close(self):
        self.driver.close()

    # def update_node(self, entity_label, properties):
    #     query:str = (
    #         f"MATCH (p:{entity_label})"
    #         f""
    #     )
