from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.search import CreatorFilterParams, CreatorSearchResult, JobFilterParams, JobSearchResult
from app.services.search_service import search_service

router = APIRouter(prefix="/api/search", tags=["Search & Discovery"])

@router.get("/creators", response_model=CreatorSearchResult)
def search_creators(
    query: str | None = Query(None, description="Free text keyword search"),
    skill: str | None = Query(None, description="Filter by skill e.g. 'Prompt Engineering'"),
    specialization: str | None = Query(None, description="Filter by specialization e.g. 'AI Video'"),
    tool: str | None = Query(None, description="Filter by tool/model e.g. 'Runway'"),
    content_type: str | None = Query(None, description="Filter by content type e.g. 'Video'"),
    aspect_ratio: str | None = Query(None, description="Filter by aspect ratio e.g. '16:9'"),
    format: str | None = Query(None, description="Filter by format e.g. 'MP4'"),
    tag: str | None = Query(None, description="Filter by tag"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    params = CreatorFilterParams(
        query=query,
        skill=skill,
        specialization=specialization,
        tool=tool,
        content_type=content_type,
        aspect_ratio=aspect_ratio,
        format=format,
        tag=tag,
        page=page,
        limit=limit
    )
    return search_service.search_creators(db, params)

@router.get("/jobs", response_model=JobSearchResult)
def search_jobs(
    query: str | None = Query(None, description="Free text keyword search"),
    content_type: str | None = Query(None, description="Filter by content type e.g. 'Video'"),
    specialization: str | None = Query(None, description="Filter by specialization"),
    skill: str | None = Query(None, description="Filter by required skill"),
    tool: str | None = Query(None, description="Filter by required tool"),
    status: str | None = Query("published", description="Filter by status"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    params = JobFilterParams(
        query=query,
        content_type=content_type,
        specialization=specialization,
        skill=skill,
        tool=tool,
        status=status,
        page=page,
        limit=limit
    )
    return search_service.search_jobs(db, params)
