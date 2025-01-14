from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    postgres_database_url: str
    secret: str
    algorithm: str
    neo4j_uri: str
    neo4j_user: str
    neo4j_pass: str
    neo4j_bb: str
    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_settings():
    return Settings()
