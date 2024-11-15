from fastapi import APIRouter

router = APIRouter(prefix="/mapper",
    tags=["mapper"],)

@router.post("/")
def create_mapper():
    return {"mapper": "true"}