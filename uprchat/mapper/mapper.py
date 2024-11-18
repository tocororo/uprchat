from .mapping_config.mapping_config import load_config_file
from .neo4j.repository import Neo4jRepository


class Mapper:
    def __init__(self, config_file, data):
        self.config = load_config_file(config_file)
        self.data = data

    def start(self):
        for entities in self.config.entities:
            pass

    def map_instances(entity, entity_data):
        if entity_data is not None:
            for item in entity_data:
                pass
