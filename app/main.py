from fastapi import FastAPI
from .db_config import create_db_and_tables
from .routes import urls, domains, sources, models, collectors, jobs, users, chats,llmqueries


app = FastAPI(title="UPR-K API", version="1.0.0")


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
