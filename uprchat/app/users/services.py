from uprchat.app.schemas import UserCreate
from sqlmodel import Session
from .utils import exist_user
from uprchat.app.models import User


async def login():
    pass

async def register_user(user_create: UserCreate, session: Session):
    user = exist_user(user_create.username,session)
    if(not user):
       user_db = User(username=user_create.username)
       session.add(user_db)
       session.commit()
       session.refresh(user_db)
       return user_db