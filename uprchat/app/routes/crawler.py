import re
from fastapi import APIRouter
from uprchat.harvester.crawler import start
from uprchat.harvester.db_services.repository import HarvesterRepository
from uprchat.harvester.graphbuilder import start_recollection

rt = APIRouter(prefix="/crawler", tags=["crawler"])


@rt.post("/")
def start_crawl():
    print("--------------------------------------------------------")
    # try:
    start()
    # except Exception as e:
    #     print(e)

@rt.post('/v2')
async def start_crawl_v2(url: str):
    print("--------------------------------------------------------")
    start_recollection(url)
    return {"message": "Crawling started"}

@rt.get("/")
def get_all_saved_data():
    return HarvesterRepository().get_all_data()
