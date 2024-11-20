from uprchat.mapper.mapping_config.mapping_config import (
    load_config_file,
    MappingConfig,
    EntityMapping,
)
from uprchat.mapper.neo4j.repository import Neo4jRepository
from uprchat.app.config import get_settings
from .types.mapper_types import Node, NestedNode
import uuid as uuid_pkg
import json


class Mapper:
    def __init__(self, config_file, data_file):
        self.config: MappingConfig = load_config_file(config_file)
        self.data = json.loads(data_file)
        self.relations = []
        self.st = get_settings()
        self.repository = Neo4jRepository(
            self.st.neo4j_uri, self.st.neo4j_user, self.st.neo4j_pass
        )

    def start(self):
        for entity_config in self.config.entities:
            print("_______the entity config")
            print(entity_config.required)

            # self.repository.drop_graph()
            self.map_instances(
                entity_config, self.data
            )  # TODO: get the corresponding data fro each use case(entity)

        print("all relations:", self.relations)
        if self.relations:
            for relation in self.relations:
                # {"fromLabel":node.label,"fromId": node.id, "toId": target_id,"targetLabel": target_label,"label": relation_label}
                print("the relation : ", relation)
                self.repository.add_relation(
                    relation.get("fromId"),
                    relation.get("fromLabel"),
                    relation.get("toId"),
                    relation.get("targetLabel"),
                    relation.get("label"),
                )

    def map_instances(self, entity_config: EntityMapping, entity_data: dict):
        if entity_data is not None:
            for item in entity_data:
                print("________the item of the data__________")
                print(item)
                node = Node(entity_config.name, item.get("id"))
                # node.properties.update(node.id)#TODO improve the

                if entity_config.validate_required(item):
                    self.process_data_properties_in_instance(
                        entity_config.properties, item, node
                    )

                self.repository.add_node(node)
                if node.nested_nodes:
                    for nested_node in node.nested_nodes:
                        self.repository.add_node(nested_node)
                        self.repository.add_relation(
                            node.id,
                            node.label,
                            nested_node.id,
                            nested_node.label,
                            "HAS",
                        )

    def process_data_properties_in_instance(
        self, properties_config: dict, data_instance: dict, node: Node
    ):
        for property_key in properties_config.keys():
            value = data_instance.get(property_key)
            if value:
                self._process_property(property_key, value, properties_config, node)

    def _process_property(
        self, property_key: str, property_value, properties_config: dict, node: Node
    ):
        if "__relation" in properties_config[property_key]:
            if isinstance(property_value, list):
                print("process relation...")
                for relation in property_value:
                    if isinstance(relation, dict):

                        self._process_relation(
                            property_key, relation, properties_config, node
                        )
            elif isinstance(property_value, dict):
                self._process_relation(
                    property_key, property_value, properties_config, node
                )

        # Literal
        elif isinstance(property_value, str):
            self._process_primitive_types(
                property_key, property_value, properties_config, node
            )

        # Dict
        elif isinstance(property_value, dict):
            print("process dict")
            self._process_dict(property_key, property_value, properties_config, node)

        elif isinstance(property_value, list):
            self._process_list(property_key, property_value, properties_config, node)

    def _process_dict(
        self, property_key, property_value, properties_config: dict, node: Node
    ):
        property_config_value = properties_config.get(property_key)
        if isinstance(property_config_value, dict) and isinstance(property_value, dict):

            nested_node = NestedNode(property_key, uuid_pkg.uuid4(), node.id)

            for new_key in property_config_value.keys():
                if property_value.get(new_key) and isinstance(
                    property_value.get(new_key), str
                ):
                    self._process_primitive_types(
                        new_key,
                        property_value.get(new_key),
                        property_config_value,
                        nested_node,
                    )

                elif property_value.get(new_key) and isinstance(
                    property_value.get(new_key), list
                ):
                    self._process_list(
                        new_key, property_value, property_config_value, nested_node
                    )

                elif property_value.get(new_key) and isinstance(
                    property_value.get(new_key), dict
                ):
                    self._process_dict(
                        new_key,
                        property_value.get(new_key),
                        property_config_value,
                        nested_node,
                    )

            if nested_node.properties:
                node.nested_nodes.append(nested_node)

    def _process_list(
        self, property_key, property_value, property_config: dict, node: Node
    ):
        dict_config = property_config.get(property_key)
        if isinstance(property_value[0], dict) and isinstance(dict_config, dic):
            for dic in property_value:
                self._process_dict(property_key, dic, dict_config, node)

        elif isinstance(property_value[0], str):
            self._process_primitive_types(
                property_key, property_value, property_config, node
            )

    def _process_primitive_types(
        self, property_key, property_value, properties_config, node: Node | NestedNode
    ):
        node.properties.update({properties_config.get(property_key): property_value})

    def _process_relation(
        self, property_key, target_object: dict, properties_config: dict, node: Node
    ):
        print(f"Processing relation: {property_key}")
        relation_config: dict = properties_config.get(property_key)
        target_id = target_object.get(relation_config.get("__relation"))
        target_label = relation_config.get("__target")
        relation_label = relation_config.get("__relation_label")

        self.relations.append(
            {
                "fromLabel": node.label,
                "fromId": node.id,
                "toId": target_id,
                "targetLabel": target_label,
                "label": relation_label,
            }
        )

    # def _process_identifiers_dict(self, subject, identifiers_dict: dict, identifiers_config:
    # dict, valuesof_config: dict):
    #     pass
