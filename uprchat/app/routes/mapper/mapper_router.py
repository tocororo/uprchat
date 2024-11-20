from fastapi import APIRouter, File
from typing import Annotated

from uprchat.mapper.neo4j.repository import Neo4jRepository
from uprchat.app.config import get_settings
from uprchat.mapper.mapper import Mapper

router = APIRouter(
    prefix="/mapper",
    tags=["mapper"],
)


@router.post("/")
def create_mapper():
    return {"mapper": "true"}


@router.post("/add")
def create(configFile: Annotated[bytes, File()], dataFile: Annotated[bytes, File()]):
    mapper = Mapper(configFile, dataFile)
    mapper.start()
