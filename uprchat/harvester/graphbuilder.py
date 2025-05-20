
import json
from typing import Dict, Optional
from uprchat.harvester.extractor import Extractor, ExtractorLLM
from uprchat.harvester.logger import setup_logger
from uprchat.mapper.services import RepositoryService, MapperService

logger = setup_logger(__name__)

class GraphBuilder:
    """
    Orchestrates a breadth-first crawl of web pages, extracting content and discovering internal links.
    Attributes:
        extractor (Extractor):   Instance responsible for fetching and parsing page data.
        extractor_ai (ExtractorLLM):   Instance responsible for fetching and parsing page data using AI.
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
        
        self.extractor = Extractor(proxy_config)
        self.extractor_ai = ExtractorLLM(
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

    async def _crawl(self, url: str, extractor: Extractor, recollection_deep: int):
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
                logger.info(f"Making request to {current_url}")
                result = await extractor.process_url(current_url)
                self.visited.add(current_url)
                if not result:
                    continue
                links = result.get("links", None)
                if links:
                    internal_links = [
                        item["href"]
                        for item in links
                        if item["href"] not in self.visited
                    ]
                    if internal_links:
                        new_urls.extend(internal_links)
                logger.info(f"Extracted data: {result}")
            self.urls.append(new_urls)

    async def start_recollection(
        self, url: str, recollection_deep: int = 99999999
    ):
        """
        Begins asynchronous crawling from a seed URL up to a specified depth, collecting page data and internal links.
        Args:
            url (str): Starting URL for the crawl.
            recollection_deep (int): Maximum number of levels to process (default: 99999999).
        Returns:
            None
        """
        await self._crawl(url, self.extractor, recollection_deep)
    
    async def start_recollection_with_ai(
        self, url: str, recollection_deep: int = 99999999
    ):
        """
        Begins asynchronous crawling from a seed URL up to a specified depth, collecting page data and internal links.
        Args:
            url (str): Starting URL for the crawl.
            recollection_deep (int): Maximum number of levels to process (default: 99999999).
        Returns:
            None
        """
        await self._crawl(url, self.extractor_ai, recollection_deep)

    def add_nodes(self, nodes: list):
        """
        Adds nodes to the Neo4j database.
        Args:
            nodes (list): List of nodes to be added.
        Returns:
            None
        """
        RepositoryService().clean_graph_db()
        with open("uprchat/harvester/mapping_document.json", "r", encoding="utf-8") as f:
            config = f.read()
            data = json.dumps(nodes)
            m_service: MapperService = MapperService(
                config,
                data
            )
            m_service.start_mapping()

