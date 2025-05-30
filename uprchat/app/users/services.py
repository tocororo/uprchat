from .schemas import UserCreate
from sqlmodel.ext.asyncio.session import AsyncSession
from .utils import get_user_data
from uprchat.app.database.models import User


async def login():
    return True

async def register_user(user_create: UserCreate, session: AsyncSession):
    user = await get_user_data(user_create.username,session)
    if(not user):
       user_db = User(username=user_create.username)
       session.add(user_db)
       await session.commit()
       await session.refresh(user_db)
       return user_db