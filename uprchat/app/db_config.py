from sqlmodel import create_engine, Session
from .models import SQLModel

from .config import get_settings


url = get_settings().postgres_database_url
engine = create_engine(url)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    with Session(engine) as session:
        return session
