from pydantic import BaseModel
from uuid import UUID


class User(BaseModel):
    username: str
    data: dict = None

class UserCreate(User):
    pass

class UserLogin(User):
    password: str

class UserUpdate(User):
    pass

class UserDB(User):
    id: UUID