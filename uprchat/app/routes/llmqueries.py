from fastapi import APIRouter, Depends, status, HTTPException
from sqlmodel import Session
from typing import Annotated
from uprchat.app.llmqueries.schemas import LLMQueryCreate,LLMQueryDB,LLMQueryUpdate
from uprchat.app.llmqueries.services import create_llmquery,read_all_llmqueries,read_llmquery,update_llmquery,delete_llmquery
from uprchat.app.database.db_config import get_session

rt = APIRouter(prefix="/llmqueries", tags=["llmqueries"])


@rt.post("/", response_model=LLMQueryDB, status_code=status.HTTP_201_CREATED)
async def create_new_llmq(
    chat_id: int,
    session: Annotated[Session, Depends(get_session)], llmquery: LLMQueryCreate
):
    return await create_llmquery(llmquery=llmquery,session=session,chat_id=chat_id)

@rt.get('/',response_model=list[LLMQueryDB],status_code=status.HTTP_200_OK)
async def get_all_llmqueries(chat_id: int,session: Annotated[Session, Depends(get_session)],offset: int = 0, limit: int = 100):
    return await read_all_llmqueries(chat_id=chat_id,limit=limit,offset=offset,session=session)

@rt.get('/{id}',response_model=LLMQueryDB,status_code=status.HTTP_200_OK)
async def get_one_llmquery(id: int,session: Annotated[Session, Depends(get_session)]):
    result =  await read_llmquery(llmquery_id=id,session=session)
    if(result is None):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="LLMQuery not found")
    return result

@rt.put('/{id}',response_model=LLMQueryDB,status_code=status.HTTP_200_OK)
async def update_one_llmquery(id: int,llmquery_update: LLMQueryUpdate,session: Annotated[Session, Depends(get_session)]):
    return await update_llmquery(llmquery_id=id,llmquery_update=llmquery_update,session=session)

@rt.delete('/{id}',status_code=status.HTTP_204_NO_CONTENT)
async def delete_one_llmquery(id: int,session: Annotated[Session, Depends(get_session)]):
    await delete_llmquery(session=session,llmquery_id=id)