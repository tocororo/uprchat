from fastapi import APIRouter
from uprchat.harvester.crawler import start
from uprchat.harvester.db_services.repository import HarvesterRepository
import asyncio

rt = APIRouter(prefix="/crawler", tags=["crawler"])


@rt.post("/")
def start_crawl():
    print("--------------------------------------------------------")
    # try:
    start()
    # except Exception as e:
    #     print(e)

@rt.get("/")
def get_all_saved_data():
    return HarvesterRepository().get_all_data()
