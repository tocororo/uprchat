from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from uprchat.app.database.models import User
from typing import Annotated
from fastapi import Depends,HTTPException,status
from fastapi.security import OAuth2PasswordBearer
from jwt import decode,encode
from uprchat.app.config import get_settings
from datetime import datetime,timezone,timedelta
from uuid import UUID


SECRET = get_settings().secret
ALGORITHM = get_settings().algorithm

async def get_user_data(username: str, session: AsyncSession):
    result = await session.exec(select(User).where(User.username == username))
    return result.first()

def generate_token(uuid: UUID):
    data = {
        "sub": str(uuid),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=60),
    }
    access_token = encode(data, SECRET, algorithm=ALGORITHM),
    return access_token

def get_current_user_uuid(token: str):

    exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        uuid = decode(token, SECRET, algorithms=[ALGORITHM])["sub"]
        if uuid is None:
            raise exception

    except:
        raise exception

    return uuid