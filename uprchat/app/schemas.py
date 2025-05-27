from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class User(BaseModel):
    username: str

class UserCreate(User):
    pass

class UserDB(User):
    id: UUID

class Chat(BaseModel):
    id: int
    user_id: UUID

class ChatCreate(Chat):
    pass

class ChatDB(Chat):
    pass

class LLMQuery(BaseModel):
    input: dict 
    output: dict 

class LLMQueryCreate(LLMQuery):
    pass

class LLMQueryUpdate(LLMQuery):
    pass

class LLMQueryDB(LLMQuery):
    id: int
    timestamp: datetime 
    chat_id: int 