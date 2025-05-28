from fastapi import APIRouter, Depends, status, Query, HTTPException
from sqlmodel import Session, select, delete
from typing import Annotated
from uprchat.app.schemas import LLMQueryCreate,LLMQueryDB
from uprchat.app.llmqueries.services import create_llmquery
from ..models import LLMQuery
from ..db_config import get_session

rt = APIRouter(prefix="/llmqueries", tags=["llmqueries"])


@rt.post("/", response_model=LLMQueryDB, status_code=status.HTTP_201_CREATED)
async def create_llmq(
    session: Annotated[Session, Depends(get_session)], llmquery: LLMQueryCreate
):
    result = await create_llmquery(llmquery=llmquery,session=session,chat_id=1)
    return result


# @rt.get("/{chat_id}", response_model=list[LLMQuery], status_code=status.HTTP_200_OK)
# async def get_llmqs(
#     session: Annotated[Session, Depends(get_session)],
#     chat_id: int,
#     offset: int = 0,
#     limit: Annotated[int, Query(le=100)] = 100,
# ):
#     llmqs = session.exec(
#         select(LLMQuery).where(LLMQuery.chat_id == chat_id).offset(offset).limit(limit)
#     ).all()
#     return llmqs


# @rt.put("/{id}", response_model=LLMQuery, status_code=status.HTTP_200_OK)
# async def update_llmq(
#     session: Annotated[Session, Depends(get_session)], id: int, llmq: LLMQuery
# ):
#     llmq_db = session.get(LLMQuery, id)
#     if not llmq_db:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND, detail="Query not found"
#         )
#     llmq_data = llmq.model_dump(exclude_unset=True)
#     llmq_db.sqlmodel_update(llmq_data)
#     session.add(llmq_db)
#     session.commit()
#     session.refresh(llmq_db)
#     return llmq_db


# @rt.delete("/delete_llmqs/{chat_id}", status_code=status.HTTP_200_OK)
# async def delete_llmqs(session: Annotated[Session, Depends(get_session)], chat_id: int):
#     session.exec(delete(LLMQuery).where(LLMQuery.chat_id == chat_id))
#     session.commit()
#     return "Queries deleted"


# @rt.delete("/{id}", status_code=status.HTTP_200_OK)
# async def delete_llmq(session: Annotated[Session, Depends(get_session)], id: int):
#     llmq = session.get(LLMQuery, id)
#     if not llmq:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND, detail="Query not found"
#         )
#     session.delete(llmq)
#     session.commit()
#     return "Query deleted"
