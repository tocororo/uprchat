from .schemas import LLMQueryCreate,LLMQueryUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError,SQLAlchemyError
from uprchat.app.database.models import LLMQuery
from sqlmodel import select
from fastapi import HTTPException,status


async def create_llmquery(llmquery: LLMQueryCreate,chat_id: int,session: AsyncSession):
    try:
        llmquery_db = LLMQuery(**llmquery.model_dump())
        llmquery_db.chat_id = chat_id
        session.add(llmquery_db)
        await session.commit()
        await session.refresh(llmquery_db)
        return llmquery_db
    # except:
    #     raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Error creating llmquery")
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error de integridad en la base de datos: {str(e)}"
        )
    except SQLAlchemyError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error de base de datos: {str(e)}"
        )

async def read_llmquery(llmquery_id: int,session: AsyncSession):
    try:
        result = await session.exec(select(LLMQuery).where(LLMQuery.id == llmquery_id))
        return result.first()
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Error reading llmquery")

async def read_all_llmqueries(chat_id: int,offset: int, limit: int,session: AsyncSession):
    try:
        result = await session.exec(select(LLMQuery).where(LLMQuery.chat_id == chat_id).offset(offset).limit(limit))
        return result.all()
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Error reading llmqueries")

async def update_llmquery(llmquery_id: int, llmquery_update: LLMQueryUpdate, session: AsyncSession):
    try:
        llmquery = await read_llmquery(llmquery_id=llmquery_id,session=session)
        llmquery_data = llmquery_update.model_dump(exclude_unset=True)
        llmquery.sqlmodel_update(llmquery_data)
        session.add(llmquery)
        await session.commit()
        await session.refresh(llmquery)
        return llmquery
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Error updating llmquery")


async def delete_llmquery(llmquery_id: int, session: AsyncSession):
    try:
        llmquery = await read_llmquery(llmquery_id=llmquery_id,session=session)
        session.delete(llmquery)
        await session.commit()
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Error deleting llmquery")
