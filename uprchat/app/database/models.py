from sqlmodel import Field, SQLModel,Column
from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import JSON,ARRAY
from sqlalchemy.dialects.postgresql import UUID as PG_UUID


class User(SQLModel, table=True):
    id: UUID = Field(
        default_factory=uuid4,  
        primary_key=True,
        nullable=False,
        sa_type=PG_UUID(as_uuid=True)  
    )
    username: str = Field(unique=True, index=True)


class Chat(SQLModel, table=True):
    id: int | None = Field(default=None,primary_key=True)
    user_id: UUID = Field(foreign_key="user.id")


class LLMQuery(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    input: list[dict] = Field(default=[], sa_column=Column(ARRAY(JSON)))  
    output: dict = Field(default={}, sa_type=JSON)  
    timestamp: datetime = Field(default_factory=lambda: datetime.now())
    chat_id: int = Field(foreign_key="chat.id")


class CrawlerData(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    uri: str = Field(unique=True, index=True)
    title: str = Field( nullable=True)
    body: str = Field()
    # subdomain: str = Field()