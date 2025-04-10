from sqlmodel import Field, SQLModel
from datetime import datetime, timezone


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    password: str = Field()
    is_admin: bool = Field(default=False)


class ChatBase(SQLModel):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ChatCreate(ChatBase):
    pass


class Chat(ChatBase, table=True):
    user_id: int = Field(foreign_key="user.id")


class LLMQuery(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    input: str = Field()
    output: str = Field()
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    model_id: int = Field(foreign_key="model.id")
    chat_id: int = Field(foreign_key="chat.id")

    model_config = {"protected_namespaces": ()}


class Model(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    api_url: str = Field(regex=r"^https?://")
    api_key: str = Field()


class Collector(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    code_path: str = Field(unique=True, index=True)


class SourceBase(SQLModel):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    collector_id: int = Field(foreign_key="collector.id")


class Source(SourceBase, table=True):
    pass


class URL(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    url: str = Field(regex=r"^https?://", unique=True)


class JobBase(SQLModel):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Job(JobBase, table=True):
    pass


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


class SourceShow(SourceBase):
    urls: list[int]
    domains: list[int]


class JobShow(JobBase):
    sources: list[int]


class CrawlerData(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    uri: str = Field(unique=True, index=True)
    title: str = Field( nullable=True)
    body: str = Field()
    # subdomain: str = Field()
