
import json
from typing import Dict, List, Optional
from neo4j import GraphDatabase, basic_auth

from uprchat.harvester.extractor import Extractor
from uprchat.harvester.logger import setup_logger
# from hd2neo4j.services import RepositoryService, MapperService
from uprchat.harvester.utils import clean_text_for_neo4j, extract_source_information, extract_text_to_document
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
                 neo4j_config: Dict[str, str],
                 proxy_config: Optional[Dict[str, str]] = None,
                 delay: Optional[int] = 1
                  ):
        
        self.extractor = Extractor(
            model_name,
            model_type,
            base_url,
            api_key,
            proxy_config,
            delay
        )
        self.visited = set()
        self.urls = []
        if not neo4j_config:
            raise ValueError("Neo4j configuration is required.")
        self._neo4j_config = {
            "neo4j_user": neo4j_config["neo4j_user"],
            "neo4j_pass": neo4j_config["neo4j_pass"],
            "neo4j_db": neo4j_config["neo4j_db"],
            "neo4j_uri": neo4j_config["neo4j_uri"]
        }

    async def _crawl(
                     self, 
                     url: str,  
                     recollection_deep: int, 
                     recollection: str,
                     entity_extraction: Optional[bool] = False,
                     summary_creation: Optional[bool] = False,
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
                update_node = False
                node = await self.node_exists(current_url, recollection)
                old_node_recollection = node["recollection"] if node else False
                if node:
                    logger.info(f"Node for {current_url} already exists, skipping.")
                    if node.get("links", None):
                        new_urls.extend(node["links"])
                    stored_in = node["stored_in"]
                else:
                    logger.info(f"Making request to {current_url}")
                    node = await self.extractor.process_url(current_url, entity_extraction)
                    if not node:
                        continue
                    node["recollection"] = recollection
                    links = node.get("links", None)
                    if links:
                        internal_links = [
                            item["href"]
                            for item in links
                            if item["href"] not in self.visited
                        ]
                        if internal_links:
                            node["links"] = internal_links
                            new_urls.extend(internal_links)
                    stored_in = node["stored_in"]
                    update_node = True
                extension = stored_in.split(".")[-1]
                source_type = "page" if extension == "html" else "document"
                if summary_creation:
                    if node.get("summary", "") == "" or recollection != old_node_recollection:
                        logger.info(f"Extracting summary for {current_url}")
                        summary = self.extractor.extract_summary(stored_in, extension)
                        node["summary"] = clean_text_for_neo4j(summary)
                        self.delete_node_by_id(node["id"])
                        update_node = True
                        
                node = self._get_data_from_result(node, source_type)
                if not old_node_recollection or update_node:
                    self.add_nodes([node], source_type)
                self.visited.add(current_url)
                if entity_extraction and (not self.are_extracted_entities(current_url) or recollection != old_node_recollection):
                    logger.info(f"Extracting entities from {current_url}")
                    content = self.extractor.extract_document_bytes(stored_in)
                    type = stored_in.split(".")[-1]
                    document = extract_text_to_document(content, type)
                    source_type = "page" if type == "html" else "document"
                    entities = self.extractor.extract_entities(document)
                    for entity_type in entities.keys():
                        for entity in entities[entity_type]:
                            entity[source_type] = node
                    self.add_entities_nodes(entities)
                elif entity_extraction:
                    logger.info("Entities already extracted.")
            self.urls.append(new_urls)

    def are_extracted_entities(self, source_page: str) -> bool:
        """
        Checks if the extractor has extracted entities.
        Args:
            source_page (str): URL of the source page to check.
        Returns:
            bool: True if entities are extracted, False otherwise.
        """
        r_service: RepositoryService = RepositoryService()
        query = f"""MATCH (p {"{ id: \""+source_page+"\"}"})-[:REFERENCED_IN]-(n)
                RETURN n"""
        records, summary, keys = r_service.execute_external_query(query)
        if records != []:
            return True
        return False

    async def node_exists(self, url: str, recollection: str) -> Dict | None:
        """
        Checks if a node with the given URL already exists in the Neo4j database.
        Args:
            url (str): URL to check.
            recollection (str): Current recollection id.
        Returns:
            Dict | None: Returns the node properties if it exists and matches the recollection, otherwise None.
        """
        r_service: RepositoryService = RepositoryService()
        query = f"""MATCH (n) WHERE n.id = \"{url}\" RETURN n LIMIT 1"""
        records, summary, keys = r_service.execute_external_query(query)
        if records != []:
            if str(records[0]["n"]["recollection"]) == recollection:
                return records[0]["n"]._properties
            # update_query = f"MATCH (n) WHERE n.id = {url} SET n.recollection = {recollection} RETURN n"
            # r_service.execute_external_query(update_query)
        return None
            
    def _get_data_from_result(self, result: Dict, type: str) -> Dict:
        source = extract_source_information(result["id"])
        data = {
            "id": result["id"],
            "stored_in": result["stored_in"],
            "source":  source,
            "recollection": result.get("recollection", "0"),
            "summary": result.get("summary", ""),
        }
        if type == "page":
            data["title"] = clean_text_for_neo4j(result.get("title", ""))
            data["body"] = clean_text_for_neo4j(result.get("body", ""))
            data["links"] = result.get("links", [])

        return data

    async def start_recollection(
        self, 
        url: str, 
        recollection_deep: int = 99999999, 
        recollection: str = "0",
        entity_extraction: Optional[bool] = False,
        summary_creation: Optional[bool] = False,
    ):
        """
        Begins asynchronous crawling from a seed URL up to a specified depth, collecting page data and internal links.
        Args:
            url (str): Starting URL for the crawl.
            recollection_deep (int): Maximum number of levels to process (default: 99999999).
            recollection (str): Current recollection (default: "0").
            entity_extraction (bool): Whether to extract entities from the pages (default: False).
            summary_creation (bool): Whether to create summaries for the pages (default: False).
        Returns:
            None
        """
        await self._crawl(url, recollection_deep, recollection, entity_extraction, summary_creation)
    
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
        try:
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
        except FileNotFoundError as e:
            logger.error(f"ERROR: {e}")
        except Exception as e:
            logger.error(f"ERROR: {e}")


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
        r_service: RepositoryService = RepositoryService()
        # r_service: RepositoryService = RepositoryService(
        #     self._neo4j_config["neo4j_uri"],
        #     self._neo4j_config["neo4j_user"],
        #     self._neo4j_config["neo4j_pass"],
        #     self._neo4j_config["neo4j_db"]
        # )
        r_service.clean_graph_db()

    def delete_node_by_id(self, node_id):
        driver = GraphDatabase.driver(
            self._neo4j_config["neo4j_uri"], 
            auth=basic_auth(self._neo4j_config["neo4j_user"], self._neo4j_config["neo4j_pass"]))
        
        query = f"""
        MATCH (n)
        WHERE n.id = \"{node_id}\"
        DETACH DELETE n
        """

        try:
            with driver.session() as session:
                result = session.run(query)
        except Exception as e:
            raise e
        finally:
            driver.close()
