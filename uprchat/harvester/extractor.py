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
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage


from uprchat.harvester.config import PDF_DIR, DOC_DIR, PPT_DIR, HTML_DIR
from uprchat.harvester.downloader import Downloader
from uprchat.harvester.parser import Parser, ParserAI

from uprchat.harvester.utils import extract_text_to_document, get_filename_from_url
from uprchat.harvester.logger import setup_logger

logger = setup_logger(__name__)

class Extractor:
    """
    Orchestrates the downloading and parsing of documents from URLs.
    """

    def __init__(self, proxy_config: Dict[str, str] | None = None):
        self.downloader = Downloader()
        self.parser = Parser()
        self.proxy_config = proxy_config

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
        return await self._handle_content_type(content_type, content, filename, url)
    
    async def _handle_content_type(self, 
                                   content_type: str, 
                                   content: bytes, 
                                   filename: str, 
                                   url: str)  -> Dict | None:
        data = None
        if content_type == "pdf":
            path = PDF_DIR / f"{filename}.pdf"
            self.downloader.save_file(content, path)
            summary = self.parser.parse_pdf(path)
            data = {
                "type": "document",
                "url": url,
                "summary": summary,
                "stored_in": path.as_posix()
            }
        elif content_type == "docx":
            path = DOC_DIR / f"{filename}.docx"
            self.downloader.save_file(content, path)
            summary = self.parser.parse_docx(path)
            data = {
                "type": "document",
                "url": url,
                "summary": summary,
                "stored_in": path.as_posix()
            }
        elif content_type == "pptx":
            path = PPT_DIR / f"{filename}.pptx"
            self.downloader.save_file(content, path)
            summary = self.parser.parse_pptx(path)
            data = {
                "type": "document",
                "url": url,
                "summary": summary,
                "stored_in": path.as_posix()
            }
        elif content_type == "site":
            path = HTML_DIR / f"{filename}.html"
            self.downloader.save_file(content, path)
            data = await self.extraction_xpath_to_json(url)
            if data:
                data["stored_in"] = path.as_posix()
        else:
            logger.error(f"Unsupported content type: {content_type}")
        return data

    def _get_content_type(self, content_type: str) -> str:
        """
        Determines the content type based on the file extension in the URL.
        Args:
            url (str): The URL to analyze.
        Returns:
            str: Content type ('pdf', 'docx', 'pptx', 'site' or 'Unknown').
        """
        match content_type:
            case "application/pdf" | "application/octet-stream":
                return "pdf"
            case (
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                | "application/vnd.google-apps.document"
            ):
                return "docx"
            case (
                "application/vnd.openxmlformats-officedocument.presentationml.presentation"
                | "application/vnd.openxmlformats-officedocument.presentationml.slideshow"
            ):
                return "pptx"
            case "text/html" | "text/html; charset=utf-8":
                return "site"
            case _:
                return content_type

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

        base_browser = BrowserConfig(
            headless=True,
            text_mode=True,
            user_agent_mode="random",
            java_script_enabled=True,
            proxy_config=self.proxy_config
        )

        config = CrawlerRunConfig(
            extraction_strategy=JsonXPathExtractionStrategy(schema, verbose=True),
            exclude_all_images=True,
            page_timeout=10000000,
            cache_mode=CacheMode.BYPASS,
            js_code="window.scrollTo(0, document.body.scrollHeight);",
            delay_before_return_html=5
        )

        async with AsyncWebCrawler(config=base_browser) as crawler:
            result = await crawler.arun(url=url, config=config)
            if result is None or not result.success:
                logger.error(f"Failed to retrieve information from {url}")
                return
            logger.info(f"Successfully retrieved information from {url}")
            content = json.loads(result.extracted_content)
            info = content[0] if content else {}
            data = {
                "type": "page",
                "url": url,
                "title": info.get("title", ""),
                "summary": info.get("body", ""),
                "links": result.links.get("internal", []),
                "stored_in": ""
            }
            return data

class PageInformation(BaseModel):
    title: str = Field(..., description="the title element for the page")
    summary: str = Field(
        ..., description="The relevant information associated to the page title"
    )


class ExtractorLLM(Extractor):
    """
    Orchestrates the downloading and parsing of documents from URLs, using llms.
    """
    def __init__(
                 self, 
                 model_name: str,
                 model_type: str,
                 base_url: str,
                 api_key: str = None,
                 proxy_config: Dict[str, str] | None = None
                 ):
        super().__init__(proxy_config=proxy_config)
        if model_type != "openai":
            raise ValueError(f"Model type '{model_type}' not supported yet.")
        self.parser = ParserAI(model_name, model_type, base_url, api_key)
        self.provider = model_type
        self.model_name = model_name
        self.base_url = base_url
        self.api_key = api_key

    async def _handle_content_type(self, 
                                   content_type: str, 
                                   content: bytes, 
                                   filename: str, 
                                   url: str) -> Dict[str, str] | None:
        if content_type == "site":
            path = HTML_DIR / f"{filename}.html"
            self.downloader.save_file(content, path)
            data = await self.extraction_using_llm(url)
            data["url"] = url
            data["stored_in"] = str(path)
        else:
            data = await super()._handle_content_type(content_type, content, filename, url)
            if not data:
                return None
        extracted_text = extract_text_to_document(content, content_type)
        entities = self.extract_entities(extracted_text)
        if entities:
            data["entities"] = entities
        else:
            logger.warning(f"No entities extracted from {url}")
        return data

    def extract_entities(self, document):
        """
        Extracts entities from the document using the LLM.
        Args:
            document (Document): The document to process.
        Returns:
            dict: The extracted entities.
        """
        with open("uprchat/harvester/config/entities_schemas.json", 'r', encoding='utf-8') as file:
            text = file.read()
    
        user_prompt = f"""
            Extract all entities from the following text according to the provided schema. Return results as a JSON object with entities grouped by type, presented as plain text without any wrapping in code blocks or any characters extraneous to the raw JSON.
            Schema:
            {text}
        """
        dict_str = self.run_prompt_custom_llm(document, user_prompt)
        try:
            entities = json.loads(dict_str)
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON: {e}")
            logger.info("Trying to extract entities again")
            try:
                entities = json.loads(dict_str[7:-4])
            except Exception as error:
                logger.error(f"Error decoding JSON: {error}")
                logger.info("Trying to extract entities again")
                entities = self.extract_entities(document)
        return entities

    async def extraction_using_llm(self, url: str):
        """
        Extracts page data (title, body text, and internal links) from a URL using an LLM.
        Args:
            url (str): The web page URL to crawl and process.
        Returns:
            dict | None
        """

        schema = PageInformation.model_json_schema()

        llm_config = LLMExtractionStrategy(
                llm_config=LLMConfig(
                provider=f"{self.provider}/{self.model_name}",
                api_token=self.api_key,
                base_url=self.base_url),
                extraction_type="schema",
                schema=schema,
                instruction="""From the crawled content, extract the title element of this page and the summarize the content of the body element, write in spanish"""
            )

        base_browser = BrowserConfig(
            headless=False,
            text_mode=True,
            user_agent_mode="random",
            java_script_enabled=True,
            proxy_config=self.proxy_config
        )

        config = CrawlerRunConfig(
            extraction_strategy=llm_config,
            exclude_all_images=True,
            page_timeout=100000,
            cache_mode=CacheMode.BYPASS,
            js_code="window.scrollTo(0, document.body.scrollHeight);",
            delay_before_return_html=5
        )

        async with AsyncWebCrawler(config=base_browser) as crawler:
            result = await crawler.arun(url=url, config=config)
            if result is None or not result.success:
                logger.error(f"Failed to retrieve information from {url}")
                return
            logger.info(f"Successfully retrieved information from {url}")
            llm_config.show_usage()
            content = json.loads(result.extracted_content)
            info = content[0] if content else {}
            data = {
                "type": "page",
                "url": url,
                "title": info.get("title", ""),
                "summary": info.get("summary", ""),
                "links": result.links.get("internal", []),
            }
            return data
    
    def run_prompt_custom_llm(self, document, user_prompt):
        llm = ChatOpenAI(
            model=self.model_name,
            base_url=self.base_url, 
            api_key=self.api_key
        )
        
        system_message = "You are an expert reader. Using only the following document content, answer the prompt precisely."
        
        messages = [
            SystemMessage(content=system_message),
            HumanMessage(content=f"""Document:
            {document.page_content}
            Prompt:
            {user_prompt}""")
        ]
        
        # Llamada directa al LLM (LLMChain está deprecado)
        response = llm.invoke(messages)
        return response.content
