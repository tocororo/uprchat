from fastapi import APIRouter, Depends, status, Query, HTTPException
from sqlmodel import Session, select
from typing import Annotated
from ..models import Domain
from ..db_config import get_session

rt = APIRouter(prefix="/domains", tags=["domains"])


def exist_domain(session: Annotated[Session, Depends(get_session)], domain_url: str):
    statement = select(Domain).filter(Domain.domain_url == domain_url)
    result = session.exec(statement).first()
    return result


@rt.post("/", response_model=Domain, status_code=status.HTTP_201_CREATED)
async def create_domain(
    session: Annotated[Session, Depends(get_session)], domain: Domain
):
    if not exist_domain(session, domain.domain_url):
        session.add(domain)
        session.commit()
        session.refresh(domain)
        return domain
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="That domain already exists"
        )


@rt.get("/", response_model=list[Domain], status_code=status.HTTP_200_OK)
async def get_domains(
    session: Annotated[Session, Depends(get_session)],
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    domains = session.exec(select(Domain).offset(offset).limit(limit)).all()
    return domains


@rt.get("/{id}", response_model=Domain, status_code=status.HTTP_200_OK)
async def get_domain_by_id(session: Annotated[Session, Depends(get_session)], id: int):
    domain = session.get(Domain, id)
    if not domain:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Domain not found"
        )
    return domain


@rt.put("/{id}", response_model=Domain, status_code=status.HTTP_200_OK)
async def update_domain(
    session: Annotated[Session, Depends(get_session)], id: int, domain: Domain
):
    domain_db = session.get(Domain, id)
    if not domain_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="URL not found"
        )
    domain_data = domain.model_dump(exclude_unset=True)
    domain_db.sqlmodel_update(domain_data)
    session.add(domain_db)
    session.commit()
    session.refresh(domain_db)
    return domain_db


@rt.delete("/{id}", status_code=status.HTTP_200_OK)
async def delete_domain(session: Annotated[Session, Depends(get_session)], id: int):
    domain = session.get(Domain, id)
    if not domain:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="URL not found"
        )
    session.delete(domain)
    session.commit()
    return "Domain deleted"
