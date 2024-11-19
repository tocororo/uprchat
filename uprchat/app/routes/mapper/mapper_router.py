from fastapi import APIRouter, UploadFile

from uprchat.mapper.neo4j.repository import Neo4jRepository
from uprchat.app.config import get_settings

router = APIRouter(
    prefix="/mapper",
    tags=["mapper"],
)


@router.post("/")
def create_mapper():
    return {"mapper": "true"}


@router.get("/add")
def create(configFIle: UploadFile, dataFile: UploadFile):
    print("Clicked on add")
