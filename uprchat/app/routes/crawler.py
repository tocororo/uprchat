
from fastapi import APIRouter
from uprchat.app.config import get_settings
from uprchat.harvester.crawler import start
from uprchat.harvester.db_services.repository import HarvesterRepository
from uprchat.harvester.graphbuilder import GraphBuilder


rt = APIRouter(prefix="/crawler", tags=["crawler"])

settings = get_settings()

async def start_recollection(url: str):
    graph_builder = GraphBuilder(
        model_name=settings.mainmodel,
        base_url=settings.base_url,
        api_key=settings.model_api_key,
        model_type="openai"
    )
    await graph_builder.start_recollection_with_ai(url)

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
