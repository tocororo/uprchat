from sqlmodel import create_engine,Session
from .models import SQLModel
import os

DB_URL = os.getenv("POSTGRES_DATABASE_URL")

engine = create_engine(DB_URL)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
