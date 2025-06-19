from .schemas import UserCreate,UserUpdate
from sqlmodel.ext.asyncio.session import AsyncSession
from .utils import get_user_data
from uprchat.app.database.models import User
from fastapi import HTTPException,status


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
    
async def update_user_data(user_data: UserUpdate,session: AsyncSession):
    try:

        user = await get_user_data(user_data.username,session)
        user_update = user_data.model_dump()
        user.sqlmodel_update(user_update)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Error updating user data")
    