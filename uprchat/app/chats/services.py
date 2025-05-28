from sqlmodel import Session,select
from uprchat.app.database.models import Chat
from fastapi import HTTPException, status
from uuid import UUID


async def create_chat(user_id: UUID ,session: Session):
    try:
        chat_db = Chat(user_id=user_id)
        session.add(chat_db)
        session.commit()
        session.refresh(chat_db)
        return chat_db
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Error creating chat")
    

async def read_chat(chat_id: int, session: Session):
    try:
        result = session.exec(select(Chat).where(Chat.id == chat_id)).first()
        return result
    except :
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Error reading chat")

async def read_all_chats(user_id: UUID,offset: int, limit: int, session: Session):
    try:
        result = session.exec(select(Chat).where(Chat.user_id == user_id).offset(offset).limit(limit)).all()
        if(not result):
            return []
        return result
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Error reading chats")

async def delete_chat(chat_id: int,session: Session):
    try:
        chat = await read_chat(chat_id=chat_id,session=session)
        session.delete(chat)
        session.commit()
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Error deleting chat")