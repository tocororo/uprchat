from fastapi import APIRouter, Depends, status, Query, HTTPException
from sqlmodel import Session, select
from typing import Annotated
from ..models import Model
from ..db_config import get_session

rt = APIRouter(prefix="/models", tags=["models"])


def exist_model(session: Annotated[Session, Depends(get_session)], name: str):
    statement = select(Model).filter(Model.name == name)
    result = session.exec(statement).first()
    return result


@rt.post("/", response_model=Model, status_code=status.HTTP_201_CREATED)
async def create_model(session: Annotated[Session, Depends(get_session)], model: Model):
    if not exist_model(session, model.name):
        session.add(model)
        session.commit()
        session.refresh(model)
        return model
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="That model already exists"
        )


@rt.get("/", response_model=list[Model], status_code=status.HTTP_200_OK)
async def get_models(
    session: Annotated[Session, Depends(get_session)],
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    models = session.exec(select(Model).offset(offset).limit(limit)).all()
    return models


@rt.get("/{id}", response_model=Model, status_code=status.HTTP_200_OK)
async def get_model_by_id(session: Annotated[Session, Depends(get_session)], id: int):
    model = session.get(Model, id)
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Model not found"
        )
    return model


@rt.put("/{id}", response_model=Model, status_code=status.HTTP_200_OK)
async def update_model(
    session: Annotated[Session, Depends(get_session)], id: int, model: Model
):
    model_db = session.get(Model, id)
    if not model_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Model not found"
        )
    model_data = model.model_dump(exclude_unset=True)
    model_db.sqlmodel_update(model_data)
    session.add(model_db)
    session.commit()
    session.refresh(model_db)
    return model_db


@rt.delete("/{id}", status_code=status.HTTP_200_OK)
async def delete_model(session: Annotated[Session, Depends(get_session)], id: int):
    model = session.get(Model, id)
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Model not found"
        )
    session.delete(model)
    session.commit()
    return "Model deleted"
