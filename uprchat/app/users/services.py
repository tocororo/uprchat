from .schemas import UserCreate
from sqlmodel import Session
from .utils import get_user_data
from uprchat.app.database.models import User


async def login():
    return True

async def register_user(user_create: UserCreate, session: Session):
    user = get_user_data(user_create.username,session)
    if(not user):
       user_db = User(username=user_create.username)
       session.add(user_db)
       session.commit()
       session.refresh(user_db)
       return user_db