from fastapi import APIRouter

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
def create():
    st = get_settings()
    r = Neo4jRepository(st.neo4j_uri, st.neo4j_user, st.neo4j_pass)

    # r.add_node("Company", {'name':'UPR', "id": "UPR_id"})
    # r.add_node("Employed", {'name':'Jorge', "id": "user_1"})
    # r.add_relation("user_1",'Employed', "UPR_id", "Company", "WORKS_FOR" )
    # r.drop_all_data()
