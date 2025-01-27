from fastapi import APIRouter
from uprchat.harvester.crawler import start_recollection
import asyncio

rt = APIRouter(prefix="/crawler", tags=["crawler"])


@rt.post("/")
async def start_crawl(url: str):
    print("--------------------------------------------------------")
    print(url)
    try:

        await start_recollection(url)
    except Exception as e:
        print(e)
