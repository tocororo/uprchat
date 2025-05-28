from uprchat.app.schemas import LLMQueryCreate,LLMQueryUpdate
from uprchat.app.models import LLMQuery
from sqlmodel import Session,select
from fastapi import HTTPException,status


async def create_llmquery(llmquery: LLMQueryCreate,chat_id: int,session: Session):
    try:
        llmquery_db = LLMQuery(**llmquery.model_dump())
        llmquery_db.chat_id = chat_id
        session.add(llmquery_db)
        session.commit()
        session.refresh(llmquery_db)
        return llmquery_db
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Error creating llmquery")

async def read_llmquery(llmquery_id: int,session: Session):
    try:
        result = session.exec(select(LLMQuery).where(LLMQuery.id == llmquery_id)).first()
        if(not result):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="LLMQuery not found")
        return result
    except:
        print(f"Error reading llmquery")

async def read_all_llmqueries(offset: int, limit: int,session: Session):
    try:
        result = session.exec(select(LLMQuery).offset(offset).limit(limit)).all()
        if(not result):
            return None
        return result
    except:
        print(f"Error reading llmqueries")

async def update_llmquery(llmquery_id: int, llmquery_update: LLMQueryUpdate, session: Session):
    try:
        llmquery = await read_llmquery(llmquery_id=llmquery_id,session=session)
        llmquery_data = llmquery_update.model_dump(exclude_unset=True)
        llmquery.sqlmodel_update(llmquery_data)
        session.add(llmquery)
        session.commit()
        session.refresh(llmquery)
        return llmquery
    except:
        print(f"Error updating llmquery")


async def delete_llmquery(llmquery_id: int, session: Session):
    try:
        llmquery = await read_llmquery(llmquery_id=llmquery_id,session=session)
        session.delete(llmquery)
        session.commit()
    except:
        print(f"Error deleting llmquery")