from fastapi import APIRouter, Depends, status, Query, HTTPException
from sqlmodel import Session, select, delete
from typing import Annotated
from ..models import Chat, ChatCreate, User
from ..db_config import get_session
from .users import current_user

rt = APIRouter(prefix="/chats", tags=["chats"])


@rt.post("/", response_model=Chat, status_code=status.HTTP_201_CREATED)
async def create_model(
    session: Annotated[Session, Depends(get_session)],
    username: Annotated[str, Depends(current_user)],
    chat: ChatCreate,
):
    user_id = session.exec(select(User).where(User.username == username)).first().id
    chat = Chat(title=chat.title, user_id=user_id)
    session.add(chat)
    session.commit()
    session.refresh(chat)
    return chat


@rt.get("/", response_model=list[Chat], status_code=status.HTTP_200_OK)
async def get_chats(
    session: Annotated[Session, Depends(get_session)],
    username: Annotated[str, Depends(current_user)],
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    user_id = session.exec(select(User).where(User.username == username)).first().id
    chats = session.exec(
        select(Chat).where(Chat.user_id == user_id).offset(offset).limit(limit)
    ).all()
    return chats


@rt.delete("/", status_code=status.HTTP_200_OK)
async def delete_chats(
    session: Annotated[Session, Depends(get_session)],
    username: Annotated[str, Depends(current_user)],
):
    user_id = session.exec(select(User).where(User.username == username)).first().id
    session.exec(delete(Chat).where(Chat.user_id == user_id))
    session.commit()
    return "Chats deleted"
