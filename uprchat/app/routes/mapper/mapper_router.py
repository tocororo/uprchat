from fastapi import APIRouter, File
from typing import Annotated
from uprchat.mapper.services import MapperService, RepositoryService

router = APIRouter(
    prefix="/mapper",
    tags=["mapper"],
)



@router.post("/")
def create_mapper():
    return {"mapper": "true"}



@router.post("/start")
def start_mapping(
    configFile: Annotated[bytes, File()], dataFile: Annotated[bytes, File()]
):
    controller = MapperService(configFile, dataFile)
    controller.start_mapping()


@router.post("/drop")
def drop_db():
    RepositoryService().clean_graph_db()
