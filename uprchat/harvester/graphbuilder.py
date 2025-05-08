
import asyncio
from uprchat.harvester.extractor import ExtractorFreeLLM, ExtractorLLM
from uprchat.harvester.logger import setup_logger

logger = setup_logger(__name__)

class GraphBuilder:
    """
    Orchestrates a breadth-first crawl of web pages, extracting content and discovering internal links.
    Attributes:
        extractor (ExtractorFreeLLM):   Instance responsible for fetching and parsing page data.
        extractor_ai (ExtractorLLM):   Instance responsible for fetching and parsing page data using AI.
        visited (set[str]):      URLs that have already been processed.
        urls (list[str]):        Queue of URLs pending extraction.
    """

    def __init__(self):
        self.extractor = ExtractorFreeLLM()
        self.extractor_ai = ExtractorLLM("openai")
        self.visited = set()
        self.urls = []

    async def start_recollection(
        self, url: str = "http://www.upr.edu.cu/home", recollection_deep: int = 99999999
    ):
        """
        Begins asynchronous crawling from a seed URL up to a specified depth, collecting page data and internal links.
        Args:
            url (str): Starting URL for the crawl (default: "http://www.upr.edu.cu/home").
            recollection_deep (int): Maximum number of levels to process (default: 99999999).
        Returns:
            None
        """
        self.urls = [url]
        iter_count = 0
        while self.urls and iter_count < recollection_deep:
            iter_count += 1
            current_url = self.urls.pop(0)
            logger.info(f"Making request to {current_url}")
            result = await self.extractor.process_url(current_url)
            self.visited.add(current_url)
            if not result:
                continue
            links = result.get("links", None)
            if links:
                internal_links = [
                    item["href"]
                    for item in links
                    if item["href"] not in self.visited and item["href"] not in self.urls
                ]
                if internal_links:
                    self.urls.extend(internal_links)
            logger.info(f"Extracted data: {result}")
    
    async def start_recollection_with_ai(
        self, url: str = "http://www.upr.edu.cu/home", recollection_deep: int = 99999999
    ):
        """
        Begins asynchronous crawling from a seed URL up to a specified depth, collecting page data and internal links.
        Args:
            url (str): Starting URL for the crawl (default: "http://www.upr.edu.cu/home").
            recollection_deep (int): Maximum number of levels to process (default: 99999999).
        Returns:
            None
        """
        self.urls = [url]
        iter_count = 0
        while self.urls and iter_count < recollection_deep:
            iter_count += 1
            current_url = self.urls.pop(0)
            logger.info(f"Making request to {current_url}")
            result = await self.extractor_ai.process_url(current_url)
            self.visited.add(current_url)
            if not result:
                continue
            links = result.get("links", None)
            if links:
                internal_links = [
                    item["href"]
                    for item in links
                    if item["href"] not in self.visited and item["href"] not in self.urls
                ]
                if internal_links:
                    self.urls.extend(internal_links)
            logger.info(f"Extracted data: {result}")


async def start_recollection(url: str):
    graph_builder = GraphBuilder()
    await graph_builder.start_recollection_with_ai(url)
