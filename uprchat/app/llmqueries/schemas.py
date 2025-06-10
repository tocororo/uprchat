from pydantic import BaseModel
from datetime import datetime


class LLMQuery(BaseModel):
    input: list[dict] 
    output: dict 

class LLMQueryCreate(LLMQuery):
    pass

class LLMQueryUpdate(LLMQuery):
    pass

class LLMQueryDB(LLMQuery):
    id: int
    timestamp: datetime 
    chat_id: int 