
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db_config import create_db_and_tables
from .routes import (
    urls,
    domains,
    sources,
    models,
    collectors,
    jobs,
    users,
    chats,
    llmqueries,
)
from .routes.mapper import mapper_router

app = FastAPI(title="UPR-K API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins= ["*"],
    allow_credentials=True,
    allow_methods= ["*"],
    allow_headers= ["*"]
)

@app.get("/")
def root():
    create_db_and_tables()
    return "Tables created"


app.include_router(urls.rt)
app.include_router(domains.rt)
app.include_router(sources.rt)
app.include_router(models.rt)
app.include_router(collectors.rt)
app.include_router(jobs.rt)
app.include_router(users.rt)
app.include_router(chats.rt)
app.include_router(llmqueries.rt)

app.include_router(mapper_router.router)


def start():
    """Launched with `poetry run start` at root level"""
    uvicorn.run("uprchat.app.main:app", host="0.0.0.0", port=8000, reload=True)
