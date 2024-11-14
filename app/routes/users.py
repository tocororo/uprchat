from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from typing import Annotated
from sqlmodel import Session, select, delete
from ..models import User
from passlib.context import CryptContext
from ..db_config import get_session
from jwt import decode, encode
from datetime import datetime, timedelta, timezone
import os


rt = APIRouter(prefix="/users", tags=["users"])

crypt = CryptContext(schemes=["bcrypt"])

SECRET = os.getenv("SECRET")

ALGORITHM = os.getenv("ALGORITHM")


def exist_user(session: Annotated[Session, Depends(get_session)], username: str):
    result = session.exec(select(User).where(User.username == username)).first()
    return result


async def current_user(token: str = Body()):

    exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        username = decode(token, SECRET, algorithms=[ALGORITHM])["sub"]
        if username is None:
            raise exception

    except:
        raise exception

    return username


@rt.post("/create", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(session: Annotated[Session, Depends(get_session)], user: User):
    if not exist_user(session, user.username):
        hash_password = crypt.hash(user.password)
        user.password = hash_password
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists"
        )


@rt.get("/", response_model=list[User], status_code=status.HTTP_200_OK)
async def get_users(
    session: Annotated[Session, Depends(get_session)],
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    users = session.exec(select(User).offset(offset).limit(limit)).all()
    return users


@rt.get("/{id}", response_model=User, status_code=status.HTTP_200_OK)
async def get_user_by_id(session: Annotated[Session, Depends(get_session)], id: int):
    user = session.exec(select(User).where(User.id == id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not exists"
        )
    return user


@rt.post("/login", response_model=dict, status_code=status.HTTP_200_OK)
async def login(session: Annotated[Session, Depends(get_session)], user: User):
    user_db = exist_user(session, user.username)
    if not user_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not exists"
        )
    if not crypt.verify(user.password, user_db.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Password incorrect"
        )
    access_token = {
        "sub": user.username,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=60),
    }
    return {
        "access_token": encode(access_token, SECRET, algorithm=ALGORITHM),
        "token_type": "bearer",
    }


@rt.patch("/change_password", response_model=str, status_code=status.HTTP_200_OK)
async def change_password(
    session: Annotated[Session, Depends(get_session)],
    username: Annotated[str, Depends(current_user)],
    new_password: Annotated[str, Body()],
):
    user = session.exec(select(User).where(User.username == username)).first()
    new_password = crypt.hash(new_password)
    user.password = new_password
    user_data = user.model_dump(exclude_unset=True)
    user.sqlmodel_update(user_data)
    session.add(user)
    session.commit()
    session.refresh(user)
    return "Password changed"


@rt.delete("/", response_model=str, status_code=status.HTTP_200_OK)
async def delete_user(
    session: Annotated[Session, Depends(get_session)],
    username: Annotated[str, Depends(current_user)],
):
    user = session.exec(select(User).where(User.username == username)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="That user not exists"
        )
    session.delete(user)
    session.commit()
    return "User deleted"
