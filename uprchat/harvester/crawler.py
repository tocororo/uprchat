from crawl4ai import AsyncWebCrawler, JsonCssExtractionStrategy, CacheMode
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig
from uprchat.harvester.schemas import CrawlerData
from uprchat.harvester.db_services.repository import HarvesterRepository
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from pydantic import BaseModel, Field
import asyncio
import json
import logging

logger = logging.getLogger(__name__)


async def start_recollection(start_url):
    browser_config = BrowserConfig(
        proxy_config={
            "server": "http://proxy.upr.edu.cu:8080",
            "username": "jorge.arencibiar",
            "password": "Dragon29*01",
        },
        user_agent_mode="random",
        verbose=True,
        browser_type="chromium",
    )
    run_config = CrawlerRunConfig()

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(url=start_url, config=run_config)
        print(result.cleaned_html)


async def start_general_recollection(start_url):
    general_schema = {
        "name": "General shema",
        "baseSelector": "html",
        "fields": [
            {"name": "rawHtml", "selector": "html", "type": "text"},
        ],
    }
    collection_strategy = JsonCssExtractionStrategy(schema=general_schema)

    js_code = "window.scrollTo(0, document.body.scrollHeight);"

    browser_config = BrowserConfig(
        headless=True,
        java_script_enabled=True,
    )

    run_config = CrawlerRunConfig(
        extraction_strategy=collection_strategy,
        cache_mode=CacheMode.ENABLED,
        exclude_external_links=True,
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        repository = HarvesterRepository()
        result = await crawler.arun(url=start_url, config=run_config)
        
        logger.info(result.extracted_content)
        links = result.links.get("internal", [])
        
        if links is not None:
            for link in links:
                uri = link.get("href")
                exist = repository.getData(uri)
                logger.info(f" the uri exist: {exist}")
                
                if exist is None:

                    logger.info(f"Recollecting: {uri}")
                    result = await crawler.arun(url=link["href"], config=run_config)
                    
                    # result.html
                    if result is not None:
                        if result.extracted_content is not None:
                            logger.info(f"The result content: {result}")
                            
                            content = json.loads(result.extracted_content)

                            logger.info(content)
                            
                            repository.saveData(
                                CrawlerData(
                                    uri=uri,
                                    title=content[0].get("title"),
                                    body=content[0].get("body"),
                                )
                            )
                            links.extend(result.links.get("internal", []))


class OpenAIModelFee(BaseModel):
    title: str = Field(..., description="the title for the article")
    body: str = Field(..., description="The relevant information associated to the article title")
    subdomain: str = Field(
        ..., description="the sub domain of the article, it can be null"
    )


async def extract_structured_data_using_llm(
    link:str, provider: str, api_token: str = None
):
    print(f"\n--- Extracting Structured Data with {provider} ---")

    if api_token is None and provider != "ollama":
        logger.error(f"API token is required for {provider}")
        return

    browser_config = BrowserConfig(headless=True)

    # extra_args = {"temperature": 0, "top_p": 0.9, "max_tokens": 2000}


    crawler_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        word_count_threshold=1,
        page_timeout=80000,
        extraction_strategy=LLMExtractionStrategy(
            provider=provider,
            api_token=api_token,
            schema=OpenAIModelFee.model_json_schema(),
            extraction_type="schema",
            instruction="""From the crawled content, extract the title for every article names along with their body content. 
            Do not miss any article in the entire content.""",
            # extra_args=extra_args,
        ),
    )
    
    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(
            url=link, config=crawler_config
        )
        print(result.extracted_content)



def start(uri: str = "https://www.upr.edu.cu"):
    asyncio.run(start_general_recollection(uri))
    # asyncio.run(extract_structured_data_using_llm(provider="ollama/llama3.3", api_token="no-token", link=uri))