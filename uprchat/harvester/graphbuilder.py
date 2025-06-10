
import json
from typing import Dict, List, Optional

from uprchat.harvester.extractor import Extractor
from uprchat.harvester.logger import setup_logger
# from hd2neo4j.services import RepositoryService, MapperService
from uprchat.harvester.utils import clean_text_for_neo4j, extract_source_information
from uprchat.mapper.services import RepositoryService, MapperService

logger = setup_logger(__name__)

class GraphBuilder:
    """
    Orchestrates a breadth-first crawl of web pages, extracting content and discovering internal links.
    Attributes:
        extractor (Extractor):   Instance responsible for fetching and parsing page data.
        visited (set[str]):      URLs that have already been processed.
        urls (list[str]):        Queue of URLs pending extraction.
    """

    def __init__(self,
                 model_name: str,
                 model_type: str,
                 base_url: str,
                 api_key: str,
                 neo4j_user: str = None,
                 neo4j_pass: str = None,
                 neo4j_db: str = None,
                 neo4j_uri: str = None,
                 proxy_config: Optional[Dict[str, str]] = None,
                  ):
        
        self.extractor = Extractor(
            model_name,
            model_type,
            base_url,
            api_key,
            proxy_config
        )
        self.visited = set()
        self.urls = []
        self._neo4j_config = {
            "neo4j_user": neo4j_user,
            "neo4j_pass": neo4j_pass,
            "neo4j_db": neo4j_db,
            "neo4j_uri": neo4j_uri
        }

    async def _crawl(
                     self, 
                     url: str,  
                     recollection_deep: int, 
                     recollection: str
                     ):
        self.visited.clear()
        self.urls = [[url]]
        iter_count = 0
        while self.urls and iter_count < recollection_deep:
            iter_count += 1
            urls_list = self.urls.pop(0)
            new_urls = []
            for current_url in urls_list:
                if current_url in self.visited: 
                    continue
                links = await self.node_exists(current_url, recollection)
                if links:
                    logger.info(f"Node for {current_url} already exists, skipping.")
                    self.urls.append(links)
                    continue
                logger.info(f"Making request to {current_url}")
                result = await self.extractor.process_url(current_url)
                self.visited.add(current_url)
                if not result:
                    continue
                result["recollection"] = recollection
                links = result.get("links", None)
                if links:
                    internal_links = [
                        item["href"]
                        for item in links
                        if item["href"] not in self.visited
                    ]
                    if internal_links:
                        result["links"] = internal_links
                        new_urls.extend(internal_links)
                element = self._get_data_from_result(result)
                self.add_nodes([element], result["type"])
                entities = result.get("entities", {})
                for entity_type in entities.keys():
                    for entity in entities[entity_type]:
                        entity["page"] = element
                self.add_entities_nodes(entities)
            self.urls.append(new_urls)

    async def node_exists(self, url: str, recollection: int) -> List | None:
        """
        Checks if a node with the given URL already exists in the Neo4j database.
        Args:
            url (str): URL to check.
            recollection (int): Current recollection number.
        Returns:
            bool: True if the node exists, False otherwise.
        """
        r_service: RepositoryService = RepositoryService()
        query = f"""MATCH (n) WHERE n.id = \"{url}\" RETURN n LIMIT 1"""
        records, summary, keys = r_service.execute_external_query(query)
        if records != []:
            if str(records[0]["n"]["recollection"]) == recollection:
                return records[0]["n"]["links"]
            # update_query = f"MATCH (n) WHERE n.id = {url} SET n.recollection = {recollection} RETURN n"
            # r_service.execute_external_query(update_query)
        return None
            
    def _get_data_from_result(self, result: Dict) -> Dict:
        source = extract_source_information(result["url"])
        summary = clean_text_for_neo4j(result["summary"])
        data = {
            "id": result["url"],
            "stored_in": result["stored_in"],
            "source":  source,
            "summary": summary,
            "recollection": result.get("recollection", "0")
        }
        if result["type"] == "page":
            data["title"] = clean_text_for_neo4j(result["title"])
            data["links"] = result["links"]

        return data

    async def start_recollection(
        self, url: str, recollection_deep: int = 99999999, recollection: str = "0"
    ):
        """
        Begins asynchronous crawling from a seed URL up to a specified depth, collecting page data and internal links.
        Args:
            url (str): Starting URL for the crawl.
            recollection_deep (int): Maximum number of levels to process (default: 99999999).
            recollection (str): Current recollection (default: "0").
        Returns:
            None
        """
        await self._crawl(url, recollection_deep, recollection)
    
    async def start_recollection_with_ai(
        self, url: str, recollection_deep: int = 99999999, recollection: str = "0"
    ):
        """
        Begins asynchronous crawling from a seed URL up to a specified depth, collecting page data and internal links.
        Args:
            url (str): Starting URL for the crawl.
            recollection_deep (int): Maximum number of levels to process (default: 99999999).
            recollection (str): Current recollection (default: "0").
        Returns:
            None
        """
        await self._crawl(url, self.extractor_ai, recollection_deep, recollection)

    def add_nodes(self, nodes: List[Dict[str, str]], entity: str) -> None:
        """
        Adds nodes to the Neo4j database.
        Args:
            nodes: List[Dict[str, str]] 
            entity: str
        Returns:
            None
        """
        with open(f'uprchat/harvester/mappings/mapping_{entity}.json', 'r') as f:
            config = f.read()
            data = json.dumps(nodes)

            m_service: MapperService = MapperService(
                config,
                data
            )
            # m_service: MapperService = MapperService(
            #     json.loads(config),
            #     nodes,
            #     RepositoryService(
            #         self._neo4j_config["neo4j_uri"],
            #         self._neo4j_config["neo4j_user"],
            #         self._neo4j_config["neo4j_pass"],
            #         self._neo4j_config["neo4j_db"]
            #     )
            # )
            m_service.start_mapping()

    def add_entities_nodes(
        self, nodes: Dict[str, List[Dict[str, str]]]
    ) -> None:
        """
        Adds nodes to the Neo4j database based on a configuration file.
        Args:
            nodes: Dict[str, List[Dict[str, str]]]
        Returns:
            None
        """
        for entity, data in nodes.items():
            self.add_nodes(data, entity)


    def clear_graph(self):
        """
        Clears the Neo4j database.
        Args:
            None
        Returns:
            None
        """
        r_service: RepositoryService = RepositoryService(
            self._neo4j_config["neo4j_uri"],
            self._neo4j_config["neo4j_user"],
            self._neo4j_config["neo4j_pass"],
            self._neo4j_config["neo4j_db"]
        )
        r_service.clean_graph_db()
