from fastapi import APIRouter, File
from typing import Annotated
from uprchat.mapper.services import MapperService, RepositoryService

router = APIRouter(
    prefix="/mapper",
    tags=["mapper"],
)


@router.get("/graph")
def get_graph():
    response = RepositoryService().get_graph()
    return response.records


@router.get("/query")
def execute_query(query: str):
    return RepositoryService().execute_external_query(query)


@router.post("/start")
def start_mapping(
    configFile: Annotated[bytes, File()], dataFile: Annotated[bytes, File()]
):
    controller = MapperService(configFile, dataFile)
    controller.start_mapping()


@router.post("/drop")
def drop_db():
    RepositoryService().clean_graph_db()
