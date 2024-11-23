from neo4j import GraphDatabase
from uprchat.mapper.types.mapper_types import Node


class Singleton:
    _instance = None

    def __new__(cls, url, user, password):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.url = url
            cls._instance.user = user
            cls._instance.password = password
        return cls._instance

class Neo4jRepository(Singleton):
    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password),database="neo4j")
        self.DATABASE = "neo4j"

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
        return self._driver.execute_query(
            query
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
        return self._driver.execute_query(query)

    def drop_graph(self):
        self._driver.execute_query(
            "MATCH (a) -[r] -> () DELETE a, r "
        )
        self._driver.execute_query("MATCH (a) DELETE a")

    def get_graph(self):
        return self._driver.execute_query("MATCH (n) RETURN n")

    def execute_external_query(
        self,
        query,
    ):
        self._driver.execute_query(query)

    def close(self):
        self._driver.close()

    # def update_node(self, entity_label, properties):
    #     query:str = (
    #         f"MATCH (p:{entity_label})"
    #         f""
    #     )
