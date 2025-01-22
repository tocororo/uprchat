
from fastapi import APIRouter
from uprchat.harvester.crawler import start_recollection
import asyncio

rt = APIRouter(prefix="/crawler", tags=["crawler"])

@rt.post("/")
async def start_crawl(url: str):
    print("--------------------------------------------------------")
    print(url)
    
    asyncio.run( start_recollection(url))
    