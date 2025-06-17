from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

from uprchat.utils.apikey_iterator import APIKeyIterator


class Settings(BaseSettings):
    mainmodel: str
    modeltxttocypher:str
    model_api_key: List[str] 
    base_url: str
    postgres_database_url: str
    postgres_user: str
    postgres_password: str
    postgres_db: str
    secret: str
    algorithm: str
    neo4j_uri: str
    neo4j_user: str
    neo4j_pass: str
    neo4j_bb: str
    proxy_server: str 
    proxy_user: str
    proxy_password: str
    model_config = SettingsConfigDict(env_file=".env")


def get_settings():
    return Settings()

settings = get_settings()

APIKeyIterator(api_keys=settings.model_api_key, 
               model_name=settings.mainmodel, 
               base_url=settings.base_url)
