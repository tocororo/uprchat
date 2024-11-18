from uprchat.mapper.mapping_config.mapping_config import (
    load_config_file,
    MappingConfig,
    EntityMapping,
)
from uprchat.mapper.neo4j.repository import Neo4jRepository
from uprchat.app.config import get_settings


class Mapper:
    def __init__(self, config_file, data):
        self.config: MappingConfig = load_config_file(config_file)
        self.data = data

    def start(self):
        for entity_config in self.config.entities:
            st = get_settings()
            r = Neo4jRepository(st.neo4j_uri, st.neo4j_user, st.neo4j_pass)
            self.map_instances(entity_config, self.data)

    def map_instances(self, entity_config: EntityMapping, entity_data):
        if entity_data is not None:
            for item in entity_data:
                if entity_config.validate_required(item):
                    self.process_data_properties_in_instance(
                        entity_config.properties, item
                    )

    def process_data_properties_in_instance(
        self, properties_config: dict, data_instance: dict
    ):
        for property_key in properties_config.keys():
            value = data_instance.get(property_key)
            if value:
                self._process_property(property_key, value, properties_config)

    def _process_property(
        self, property_key: str, property_value, properties_config: dict
    ):

        if "identifiers" == property_key and isinstance(property_value, list):
            print("process identifiers...")
            for identifier in property_value:
                self._process_identifiers_dict(
                    identifier,
                    properties_config.get("identifiers"),
                    valuesof_config,
                )
