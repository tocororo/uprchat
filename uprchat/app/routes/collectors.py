from fastapi import APIRouter, Depends, status, Query, HTTPException
from sqlmodel import Session, select
from typing import Annotated
from ..models import Collector
from ..db_config import get_session

rt = APIRouter(prefix="/collectors", tags=["collectors"])


def exist_collector(session: Annotated[Session, Depends(get_session)], code_path: str):
    statement = select(Collector).filter(Collector.code_path == code_path)
    result = session.exec(statement).first()
    return result


@rt.post("/", response_model=Collector, status_code=status.HTTP_201_CREATED)
async def create_collector(
    session: Annotated[Session, Depends(get_session)], collector: Collector
):
    if not exist_collector(session, collector.code_path):
        session.add(collector)
        session.commit()
        session.refresh(collector)
        return collector
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="That collector already exists",
        )


@rt.get("/", response_model=list[Collector], status_code=status.HTTP_200_OK)
async def get_collectors(
    session: Annotated[Session, Depends(get_session)],
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    collectors = session.exec(select(Collector).offset(offset).limit(limit)).all()
    return collectors


@rt.get("/{id}", response_model=Collector, status_code=status.HTTP_200_OK)
async def get_collector_by_id(
    session: Annotated[Session, Depends(get_session)], id: int
):
    collector = session.get(Collector, id)
    if not collector:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Collector not found"
        )
    return collector


@rt.put("/{id}", response_model=Collector, status_code=status.HTTP_200_OK)
async def update_collector(
    session: Annotated[Session, Depends(get_session)], id: int, collector: Collector
):
    collector_db = session.get(Collector, id)
    if not collector_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Collector not found"
        )
    collector_data = collector.model_dump(exclude_unset=True)
    collector_db.sqlmodel_update(collector_data)
    session.add(collector_db)
    session.commit()
    session.refresh(collector_db)
    return collector_db


@rt.delete("/{id}", status_code=status.HTTP_200_OK)
async def delete_collector(session: Annotated[Session, Depends(get_session)], id: int):
    collector = session.get(Collector, id)
    if not collector:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Collector not found"
        )
    session.delete(collector)
    session.commit()
    return "Collector deleted"
