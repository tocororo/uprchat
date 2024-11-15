from sqlmodel import create_engine, Session
from .models import SQLModel

from .config import get_settings

engine = create_engine(get_settings().postgres_database_url)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
