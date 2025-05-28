from fastapi import APIRouter, Depends, status, HTTPException
from sqlmodel import Session
from typing import Annotated
from uprchat.app.schemas import ChatDB
from uprchat.app.chats.services import create_chat, read_all_chats, read_chat, delete_chat
from ..db_config import get_session
from uprchat.app.users.utils import get_current_user_uuid
from uuid import UUID


rt = APIRouter(prefix="/chats", tags=["chats"])


@rt.post("/",status_code=status.HTTP_201_CREATED,response_model=ChatDB)
async def create_new_chat(
    session: Annotated[Session, Depends(get_session)],
    user_id: Annotated[UUID,Depends(get_current_user_uuid)]
):
    return await create_chat(user_id=user_id,session=session)

@rt.get('/',status_code=status.HTTP_200_OK,response_model=list[ChatDB])
async def get_all_chats(user_id: Annotated[UUID,Depends(get_current_user_uuid)],session: Annotated[Session,Depends(get_session)], offset: int = 0, limit: int = 100):
    return await read_all_chats(session=session,offset=offset, limit=limit, user_id=user_id)

@rt.get('/{chat_id}',status_code=status.HTTP_200_OK,response_model=ChatDB)
async def get_one_chat(chat_id: int ,session: Annotated[Session,Depends(get_session)]):
    result = await read_chat(chat_id=chat_id,session=session)
    if(result is None):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Chat not found")
    return result

@rt.delete('/{chat_id}',status_code=status.HTTP_204_NO_CONTENT)
async def delete_one_chat(chat_id: int ,session: Annotated[Session,Depends(get_session)]):
    return await delete_chat(chat_id=chat_id,session=session)
