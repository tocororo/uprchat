from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from uprchat.app.database.models import Chat
from fastapi import HTTPException, status
from uuid import UUID


async def create_chat(user_id: UUID ,session: AsyncSession):
    try:
        chat_db = Chat(user_id=user_id)
        session.add(chat_db)
        await session.commit()
        await session.refresh(chat_db)
        return chat_db
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Error creating chat")
    

async def read_chat(chat_id: int, session: AsyncSession):
    try:
        result = await session.exec(select(Chat).where(Chat.id == chat_id))
        return result.first()
    except :
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Error reading chat")

async def read_all_chats(user_id: UUID,offset: int, limit: int, session: AsyncSession):
    try:
        result = await session.exec(select(Chat).where(Chat.user_id == user_id).offset(offset).limit(limit))
        if(not result):
            return []
        return result.all()
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Error reading chats")

async def delete_chat(chat_id: int,session: AsyncSession):
    try:
        chat = await read_chat(chat_id=chat_id,session=session)
        session.delete(chat)
        await session.commit()
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Error deleting chat")