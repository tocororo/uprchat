from sqlmodel import Field, SQLModel
from datetime import datetime, timezone


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    password: str = Field()


class Chat(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    user_id: int = Field(foreign_key="user.id")


class LLMQuery(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    input: str = Field()
    output: str = Field()
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    model_id: int = Field(foreign_key="model.id")
    chat_id: int = Field(foreign_key="chat.id")


class Model(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    api_url: str = Field(regex=r"^https?://")
    api_key: str = Field()


class Collector(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    code_path: str = Field(unique=True, index=True)


class Source(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)


class URL(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    url: str = Field(regex=r"^https?://", unique=True)


class Job(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Domain(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    domain_url: str = Field(
        unique=True,
        regex=r"^(?!-)(xn--)?[a-z0-9][a-z0-9-_]{0,61}[a-z0-9]{0,}\.?(xn--)?([a-z0-9\-]{1,61}|[a-z0-9-]{1,30})\.[a-z]{2,}$",
    )


class Source_URL(SQLModel, table=True):
    source_id: int = Field(foreign_key="source.id", primary_key=True)
    url_id: int = Field(foreign_key="url.id", primary_key=True)


class Source_Domain(SQLModel, table=True):
    source_id: int = Field(foreign_key="source.id", primary_key=True)
    domain_id: int = Field(foreign_key="domain.id", primary_key=True)


class Source_Job(SQLModel, table=True):
    source_id: int = Field(foreign_key="source.id", primary_key=True)
    job_id: int = Field(foreign_key="job.id", primary_key=True)
