from pydantic import BaseModel
from uuid import UUID


class Chat(BaseModel):
    user_id: UUID

class ChatCreate(Chat):
    pass

class ChatDB(Chat):
    id: int