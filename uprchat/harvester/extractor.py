import json
from typing import Dict

from crawl4ai import (
    AsyncWebCrawler,
    BrowserConfig,
    CacheMode,
    CrawlerRunConfig,
    JsonXPathExtractionStrategy,
    LLMConfig,
    LLMExtractionStrategy,
)

from uprchat.harvester.config import PDF_DIR, DOC_DIR, PPT_DIR, PageInformation
from uprchat.harvester.downloader import Downloader
from uprchat.harvester.parser import Parser, ParserAI
from uprchat.harvester.config import llms_providers

# from config import get_settings
from uprchat.harvester.utils import get_filename_from_url
from uprchat.harvester.logger import setup_logger

logger = setup_logger(__name__)


class ExtractorFreeLLM:
    """
    Orchestrates the downloading and parsing of documents from URLs.
    """

    def __init__(self):
        self.downloader = Downloader()
        self.parser = Parser()

    async def process_url(self, url: str) -> Dict | None:
        """
        Processes a single URL
        Args:
            url (str): The URL to process.
        """
        response = self.downloader.fetch(url)

        content = response.get("content", None)
        if not content:
            logger.error(f"No content fetched from {url}")
            return None

        filename = get_filename_from_url(url)
        content_type = self._get_content_type(response.get("content-type", ""))
        if content_type == "pdf":
            path = PDF_DIR / f"{filename}.pdf"
            self.downloader.save_file(content, path)
            summary = self.parser.parse_pdf(path)
            data = {
                "type": "document",
                "url": url,
                "summary": summary,
                "stored_in": str(path),
            }
        elif content_type == "docx":
            path = DOC_DIR / f"{filename}.docx"
            self.downloader.save_file(content, path)
            summary = self.parser.parse_docx(path)
            data = {
                "type": "document",
                "url": url,
                "summary": summary,
                "stored_in": str(path),
            }
        elif content_type == "pptx":
            path = PPT_DIR / f"{filename}.pptx"
            self.downloader.save_file(content, path)
            summary = self.parser.parse_pptx(path)
            data = {
                "type": "document",
                "url": url,
                "summary": summary,
                "stored_in": str(path),
            }
        elif content_type == "site":
            data = await self.extraction_xpath_to_json(url)
        else:
            logger.error(f"Unsupported content type: {content_type}")
            return None
        return data

    def _get_content_type(self, content_type: str) -> Dict:
        """
        Determines the content type based on the file extension in the URL.
        Args:
            url (str): The URL to analyze.
        Returns:
            str: Content type ('pdf', 'docx', 'pptx', or 'site').
        """
        match content_type:
            case "application/pdf" | "application/octet-stream":
                return "pdf"
            case (
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                | "application/vnd.google-apps.document "
            ):
                return "docx"
            case (
                "application/vnd.openxmlformats-officedocument.presentationml.presentation"
                | "application/vnd.openxmlformats-officedocument.presentationml.slideshow"
            ):
                return "pptx"
            case "application/vnd.ms-powerpoint":
                return content_type
            case "application/msword" | "application/rtf":
                return content_type
            case _:
                return "site"

    async def extraction_xpath_to_json(self, url: str):
        """
        Extracts page data (title, body text, and internal links) from a URL using an XPath‐based JSON schema.
        Args:
            url (str): The web page URL to crawl and process.
        Returns:
            dict | None
        """
        schema = {
            "name": "Data in plain text",
            "baseSelector": "/html",
            "fields": [
                {"name": "title", "selector": "//title", "type": "text"},
                {
                    "name": "body",
                    "selector": "//body//*[not(self::style or self::script)]",
                    "type": "text",
                },
            ],
        }

        # settings = get_settings()

        base_browser = BrowserConfig(
            headless=False,
            text_mode=True,
            user_agent_mode="random",
            java_script_enabled=True,
            # proxy_config={
            #     "server": settings.proxy_server,
            #     "username": settings.proxy_user,
            #    "password": settings.proxy_password,
            # }
        )

        config = CrawlerRunConfig(
            extraction_strategy=JsonXPathExtractionStrategy(schema, verbose=True),
            exclude_all_images=True,
            page_timeout=100000,
            cache_mode=CacheMode.BYPASS,
            wait_for="5",
            js_code="window.scrollTo(0, document.body.scrollHeight);",
        )

        async with AsyncWebCrawler(config=base_browser) as crawler:
            result = await crawler.arun(url=url, config=config)
            if result is None or not result.success:
                logger.error(f"Failed to retrieve information from {url}")
                return
            logger.info(f"Successfully retrieved information from {url}")
            content = json.loads(result.extracted_content)
            data = {
                "type": "page",
                "url": url,
                "title": content[0].get("title", ""),
                "body": content[0].get("body", ""),
            }
            internal_links = result.links.get("internal", [])
            data["links"] = internal_links
            return data


class ExtractorLLM:
    """
    Orchestrates the downloading and parsing of documents from URLs, using llms.
    """

    def __init__(self, provider: str):
        self.provider = provider
        self.downloader = Downloader()
        self.parser = ParserAI(provider)


    async def process_url(self, url: str) -> Dict | None:
        """
        Processes a single URL
        Args:
            url (str): The URL to process.
        """
        response = self.downloader.fetch(url)

        content = response.get("content", None)
        if not content:
            logger.error(f"No content fetched from {url}")
            return None

        filename = get_filename_from_url(url)
        content_type = self._get_content_type(response.get("content-type", ""))
        if content_type == "pdf":
            path = PDF_DIR / f"{filename}.pdf"
            self.downloader.save_file(content, path)
            summary = self.parser.parse_pdf(path)
            data = {
                "type": "document",
                "url": url,
                "summary": summary,
                "stored_in": str(path),
            }
        elif content_type == "docx":
            path = DOC_DIR / f"{filename}.docx"
            self.downloader.save_file(content, path)
            summary = self.parser.parse_docx(path)
            data = {
                "type": "document",
                "url": url,
                "summary": summary,
                "stored_in": str(path),
            }
        elif content_type == "pptx":
            path = PPT_DIR / f"{filename}.pptx"
            self.downloader.save_file(content, path)
            summary = self.parser.parse_pptx(path)
            data = {
                "type": "document",
                "url": url,
                "summary": summary,
                "stored_in": str(path),
            }
        elif content_type == "site":
            data = await self.extraction_using_llm(url)
        else:
            logger.error(f"Unsupported content type: {content_type}")
            return None
        return data

    def _get_content_type(self, content_type: str) -> Dict:
        """
        Determines the content type based on the file extension in the URL.
        Args:
            url (str): The URL to analyze.
        Returns:
            str: Content type ('pdf', 'docx', 'pptx', or 'site').
        """
        match content_type:
            case "application/pdf" | "application/octet-stream":
                return "pdf"
            case (
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                | "application/vnd.google-apps.document "
            ):
                return "docx"
            case (
                "application/vnd.openxmlformats-officedocument.presentationml.presentation"
                | "application/vnd.openxmlformats-officedocument.presentationml.slideshow"
            ):
                return "pptx"
            case "application/vnd.ms-powerpoint":
                return content_type
            case "application/msword" | "application/rtf":
                return content_type
            case _:
                return "site"

    async def extraction_using_llm(self, url: str):
        """
        Extracts page data (title, body text, and internal links) from a URL using an XPath‐based JSON schema.
        Args:
            url (str): The web page URL to crawl and process.
        Returns:
            dict | None
        """

        schema = PageInformation.model_json_schema()

        if self.provider != "ollama":
            llm_config = LLMExtractionStrategy(
                llm_config=LLMConfig(
                provider=f"{self.provider}/{llms_providers[self.provider]['name']}",
                api_token=llms_providers[self.provider]["api_key"],
                base_url="https://apigateway.avangenio.net"),
                extraction_type="schema",
                schema=schema,
                instruction="""From the crawled content, extract the title element of this page and the summarize the content of the body element"""
            )
        else:
            llm_config = LLMExtractionStrategy(
                provider=f"ollama/{llms_providers[self.provider]['name']}",
                extraction_type="schema",
                schema=schema,
                instruction="""From the crawled content, extract the title for every article names along with their body content. 
                Do not miss any article in the entire content."""
            )

        # settings = get_settings()

        base_browser = BrowserConfig(
            headless=False,
            text_mode=True,
            user_agent_mode="random",
            java_script_enabled=True,
            # proxy_config={
            #     "server": settings.proxy_server,
            #     "username": settings.proxy_user,
            #    "password": settings.proxy_password,
            # }
        )

        config = CrawlerRunConfig(
            extraction_strategy=llm_config,
            exclude_all_images=True,
            page_timeout=100000,
            cache_mode=CacheMode.BYPASS,
            wait_for="5",
            js_code="window.scrollTo(0, document.body.scrollHeight);",
        )

        async with AsyncWebCrawler(config=base_browser) as crawler:
            result = await crawler.arun(url=url, config=config)
            if result is None or not result.success:
                logger.error(f"Failed to retrieve information from {url}")
                return
            logger.info(f"Successfully retrieved information from {url}")
            content = json.loads(result.extracted_content)
            llm_config.show_usage()
            data = {
                "type": "page",
                "url": url,
                "title": content[0].get("title", ""),
                "body": content[0].get("body", ""),
            }
            internal_links = result.links.get("internal", [])
            data["links"] = internal_links
            return data