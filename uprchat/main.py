import uvicorn
from fastapi import FastAPI
from app.routes.mapper import mapper_router
app = FastAPI()

app.include_router(mapper_router.router)

@app.get("/")
async def root():
    return {"message": "Hello Upr Chat"}


# def start():
#     """Launched with `poetry run start` at root level"""
#     uvicorn.run("uprchat.main:app", host="0.0.0.0", port=8000, reload=True)