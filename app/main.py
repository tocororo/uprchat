from fastapi import FastAPI
from .db_config import create_db_and_tables
from .routes import urls


app = FastAPI(title="UPR-K API",version='1.0.0')

@app.get("/")
def root():
    create_db_and_tables()
    return "Tables created"

app.include_router(urls.rt)
