from fastapi import APIRouter, Depends, status, Query, HTTPException
from sqlmodel import Session, select
from typing import Annotated
from ..models import Source, Source_Domain, Source_URL, SourceShow, URL, Domain
from ..db_config import get_session

rt = APIRouter(prefix="/sources", tags=["sources"])


def exist_source(session: Annotated[Session, Depends(get_session)], name: str):
    statement = select(Source).filter(Source.name == name)
    result = session.exec(statement).first()
    return result


@rt.post("/", response_model=SourceShow, status_code=status.HTTP_201_CREATED)
async def create_url(
    session: Annotated[Session, Depends(get_session)],
    source: Source,
    urls: list[int],
    domains: list[int],
):
    if not exist_source(session, source.name):
        session.add(source)
        session.commit()
        session.refresh(source)
        for id in urls:
            source_url = Source_URL(source_id=source.id, url_id=id)
            session.add(source_url)
        for id in domains:
            source_domain = Source_Domain(source_id=source.id, domain_id=id)
            session.add(source_domain)
        session.commit()
        return SourceShow(id=source.id, name=source.name, urls=urls, domains=domains)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="That source already exists"
        )


@rt.get("/", response_model=list[SourceShow], status_code=status.HTTP_200_OK)
async def get_sources(
    session: Annotated[Session, Depends(get_session)],
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    sources = session.exec(select(Source).offset(offset).limit(limit)).all()
    sources_list: list[SourceShow] = []
    for source in sources:
        statement1 = select(Source_URL).filter(Source.id == source.id)
        statement2 = select(Source_Domain).filter(Source.id == source.id)
        urls = session.exec(statement1).all()
        domains = session.exec(statement2).all()
        sources_list.append(
            SourceShow(id=source.id, name=source.name, urls=urls, domains=domains)
        )
    return sources_list


# @rt.get("/{id}", response_model=URL, status_code=status.HTTP_200_OK)
# async def get_url_by_id(session: Annotated[Session, Depends(get_session)], id: int):
#     url = session.get(URL, id)
#     if not url:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND, detail="URL not found"
#         )
#     return url


# @rt.put("/{id}", response_model=URL, status_code=status.HTTP_200_OK)
# async def update_url(
#     session: Annotated[Session, Depends(get_session)], id: int, url: URL
# ):
#     url_db = session.get(URL, id)
#     if not url_db:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND, detail="URL not found"
#         )
#     url_data = url.model_dump(exclude_unset=True)
#     url_db.sqlmodel_update(url_data)
#     session.add(url_db)
#     session.commit()
#     session.refresh(url_db)
#     return url_db


# @rt.delete("/{id}", status_code=status.HTTP_200_OK)
# async def delete_url(session: Annotated[Session, Depends(get_session)], id: int):
#     url = session.get(URL, id)
#     if not url:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND, detail="URL not found"
#         )
#     session.delete(url)
#     session.commit()
#     return "URL deleted"
