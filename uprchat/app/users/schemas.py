from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class User(BaseModel):
    username: str

class UserCreate(User):
    pass

class UserLogin(User):
    password: str

class UserDB(User):
    id: UUID