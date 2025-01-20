from .neo4j.mapper import Mapper
from .neo4j.repository import Neo4jRepository
import json
from uprchat.app.config import get_settings
from uprchat.mapper.mapping_config.mapping_config import (
    MappingConfig,
)
import logging

logger = logging.getLogger(__name__)


class RepositoryService:
    st = get_settings()
    repository = Neo4jRepository(
        st.neo4j_uri, st.neo4j_user, st.neo4j_pass, st.neo4j_bb
    )

    def __init__(self):
        super().__init__()

    def get_repository(self):
        return self.repository

    def clean_graph_db(self):
        self.repository.drop_graph()

    def execute_external_query(self, query: str):
        upper_query = query.upper()
        if (
            "MERGE" in upper_query
            or "CREATE" in upper_query
            or "DELETE" in upper_query
            or " SET " in upper_query
        ):
            return logger.error("Only consult queries are allowed")
        elif not "RETURN" in upper_query:
            return logger.error("The query must have a return statement")
        return self.repository.execute_external_query(query)

    def get_graph(self):
        return self.repository.get_graph()


class MapperService:

    def __init__(self, mapping_config_file, data_to_map_file):
        self.mapper = Mapper(
            MappingConfig(json.loads(mapping_config_file)),
            json.loads(data_to_map_file),
            RepositoryService().get_repository(),
        )

    def start_mapping(self):
        self.mapper.start()
