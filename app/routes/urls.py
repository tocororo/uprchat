from fastapi import APIRouter, Depends, status, Query, HTTPException
from sqlmodel import Session, select
from typing import Annotated
from ..models import URL
from ..db_config import get_session

rt = APIRouter(prefix="/urls", tags=["urls"])


def exist_url(session: Annotated[Session, Depends(get_session)], url: str):
    statement = select(URL).filter(URL.url == url)
    result = session.exec(statement).first()
    return result


@rt.post("/", response_model=URL, status_code=status.HTTP_201_CREATED)
async def create_url(session: Annotated[Session, Depends(get_session)], url: URL):
        if not exist_url(session,url.url):
            session.add(url)
            session.commit()
            session.refresh(url)
            return url
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="That url already exists"
            )


@rt.get("/", response_model=list[URL], status_code=status.HTTP_200_OK)
async def get_urls(
    session: Annotated[Session, Depends(get_session)],
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    urls = session.exec(select(URL).offset(offset).limit(limit)).all()
    return urls


@rt.get("/{id}", response_model=URL, status_code=status.HTTP_200_OK)
async def get_url_by_id(session: Annotated[Session, Depends(get_session)], id: int):
    url = session.get(URL, id)
    if not url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="URL not found"
        )
    return url


@rt.put("/{id}", response_model=URL, status_code=status.HTTP_200_OK)
async def update_url(
    session: Annotated[Session, Depends(get_session)], id: int, url: URL
):
    url_db = session.get(URL, id)
    if not url_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="URL not found"
        )
    url_data = url.model_dump(exclude_unset=True)
    url_db.sqlmodel_update(url_data)
    session.add(url_db)
    session.commit()
    session.refresh(url_db)
    return url_db


@rt.delete("/{id}", status_code=status.HTTP_200_OK)
async def delete_url(session: Annotated[Session, Depends(get_session)], id: int):
    url = session.get(URL, id)
    if not url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="URL not found"
        )
    session.delete(url)
    session.commit()
    return "URL deleted"
