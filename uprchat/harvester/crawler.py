from crawl4ai import AsyncWebCrawler, JsonCssExtractionStrategy, CacheMode
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig
from uprchat.app.models import CrawlerData
from uprchat.harvester.db_services.repository import HarvesterRepository
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
            {"name": "title", "selector": "title", "type": "text"},
            {"name": "body", "selector": "body", "type": "text"},
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
        print(result.extracted_content)
        links = result.links.get("internal", [])
        
        
        
        if links is not None:
            for link in links:
                uri = link.get("href")
                exist = repository.getData(uri)
                logger.info(f" the uri exist: {exist}")
                
                if exist is None:

                    logger.info(f"Recollecting: {uri}")
                    result = await crawler.arun(url=link["href"], config=run_config)
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


def start(uri: str = "https://www.upr.edu.cu"):
    asyncio.run(start_general_recollection(uri))
