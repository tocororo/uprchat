from uprchat.app.routes import crawler
import uvicorn
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from uprchat.app.database.db_config import create_tables
from .routes import chats,llmqueries,users
from .routes.mapper import mapper_router

# Use the commented implementation of the logger for customs logs
# logging.config.fileConfig('logging.conf', disable_existing_loggers=False)

logging.basicConfig(filename="logfile.log", filemode="w", level=logging.INFO)

logger = logging.getLogger("main")

app = FastAPI(title="UPR-K API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    create_tables()
    return "Tables created"


app.include_router(chats.rt)
app.include_router(crawler.rt)
app.include_router(llmqueries.rt)
app.include_router(users.rt)
app.include_router(mapper_router.router)


def start():
    """Launched with `poetry run start` at root level"""
    uvicorn.run("uprchat.app.main:app", host="0.0.0.0", port=8000, reload=True)
