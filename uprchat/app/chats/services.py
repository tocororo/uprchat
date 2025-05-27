from uprchat.app.schemas import ChatCreate
from sqlmodel import Session,select
from uprchat.app.models import Chat
from fastapi import HTTPException, status


async def create_chat(chat: ChatCreate,session: Session):
    try:
        chat_db = Chat(user_id=chat.user_id)
        session.add(chat_db)
        session.commit()
        session.refresh(chat_db)
        return chat_db
    except Exception() as e:
        print(f"Error creating chat: {e}")
    

async def read_chat(chat_id: int, session: Session):
    try:
        result = session.exec(select(Chat).where(Chat.id == chat_id)).first()
        if(not result):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Chat not found")
        return result
    except Exception() as e:
        print(f"Error reading chat: {e}")

async def read_all_chats(offset: int, limit: int, session: Session):
    try:
        result = session.exec(select(Chat).offset(offset).limit(limit)).all()
        if(not result):
            return None
        return result
    except Exception() as e:
        print(f"Error reading chats: {e}")

async def delete_chat(chat_id: int,session: Session):
    try:
        chat = await read_chat(chat_id=chat_id,session=session)
        session.delete(chat)
        session.commit()
    except Exception() as e:
        print(f"Error deleting chat: {e}")