from fastapi import APIRouter, Depends, status, Query, HTTPException
from sqlmodel import Session, select, delete
from typing import Annotated
from ..models import Job, Source_Job, JobShow
from ..db_config import get_session


rt = APIRouter(prefix="/jobs", tags=["jobs"])


def exist_job(session: Annotated[Session, Depends(get_session)], name: str):
    statement = select(Job).filter(Job.name == name)
    result = session.exec(statement).first()
    return result


@rt.post("/", response_model=Job, status_code=status.HTTP_201_CREATED)
async def create_job(
    session: Annotated[Session, Depends(get_session)],
    job: Job,
    sources: list[int],
):
    if not exist_job(session, job.name):
        session.add(job)
        session.commit()
        session.refresh(job)
        for id in sources:
            source_job = Source_Job(source_id=id, job_id=job.id)
            session.add(source_job)
        session.commit()
        return JobShow(id=job.id, name=job.name, sources=sources)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="That job already exists"
        )


@rt.get("/", response_model=list[JobShow], status_code=status.HTTP_200_OK)
async def get_jobs(
    session: Annotated[Session, Depends(get_session)],
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    jobs = session.exec(select(Job).offset(offset).limit(limit)).all()
    jobs_list: list[JobShow] = []
    for job in jobs:
        statement = select(Source_Job).filter(Source_Job.job_id == job.id)
        sources = session.exec(statement).all()
        sources_ids = []
        for i in sources:
            sources_ids.append(i.source_id)
        jobs_list.append(JobShow(id=job.id, name=job.name, sources=sources_ids))
        sources_ids.clear()
    return jobs_list


@rt.get("/{id}", response_model=JobShow, status_code=status.HTTP_200_OK)
async def get_job_by_id(session: Annotated[Session, Depends(get_session)], id: int):
    job = session.get(Job, id)
    statement = select(Source_Job).filter(Source_Job.job_id == id)
    sources = session.exec(statement).all()
    sources_ids = []
    for i in sources:
        sources_ids.append(i.source_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job not found"
        )
    return JobShow(id=job.id, name=job.name, date=job.date, sources=sources_ids)


@rt.put("/{id}", response_model=JobShow, status_code=status.HTTP_200_OK)
async def update_job(
    session: Annotated[Session, Depends(get_session)],
    id: int,
    job: Job,
    sources: list[int],
):
    job_db = session.get(Job, id)
    if not job_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job not found"
        )
    job_data = job.model_dump(exclude_unset=True)
    job_db.sqlmodel_update(job_data)
    session.add(job_db)
    session.commit()
    session.refresh(job_db)
    session.exec(delete(Source_Job).where(Source_Job.job_id == id))
    for i in sources:
        source_job = Source_Job(source_id=i, job_id=id)
        session.add(source_job)
    session.commit()
    return JobShow(id=id, name=job_db.name, date=job_db.date, sources=sources)


@rt.delete("/{id}", status_code=status.HTTP_200_OK)
async def delete_job(session: Annotated[Session, Depends(get_session)], id: int):
    job = session.get(Job, id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job not found"
        )
    session.exec(delete(Source_Job).where(Source_Job.job_id == id))
    session.delete(job)
    session.commit()
    return "Job deleted"
