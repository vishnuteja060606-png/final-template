from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User
from app.schemas.job import JobCreate, JobUpdate, JobResponse
from app.services.job_service import job_service
from app.services.company_service import company_service
from app.services.auth_service import get_current_user, get_current_user_optional, require_role

router = APIRouter(prefix="/api/jobs", tags=["Creative Briefs / Jobs"])

@router.get("", response_model=list[JobResponse])
def list_published_jobs(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional)
):
    jobs = job_service.list_published(db, limit)

    # ── Role-based isolation: companies/agencies ONLY see their own briefs ──
    if current_user and current_user.role in ["company", "agency"]:
        company_profile = company_service.get_by_user_id(db, current_user.id)
        if company_profile:
            jobs = [j for j in jobs if j.company_id == company_profile.id]
        else:
            jobs = []

    return [
        JobResponse(
            id=j.id,
            company_id=j.company_id,
            company_name=j.company.company_name if j.company else None,
            title=j.title,
            description=j.description,
            campaign_requirements=j.campaign_requirements,
            content_type=j.content_type,
            style=j.style,
            format=j.format,
            aspect_ratio=j.aspect_ratio,
            commercial_use=j.commercial_use,
            required_skills=j.required_skills,
            required_tools=j.required_tools,
            specialization=j.specialization,
            budget_range=j.budget_range,
            status=j.status,
            created_at=j.created_at,
            updated_at=j.updated_at
        )
        for j in jobs
    ]

@router.get("/my", response_model=list[JobResponse])
def list_my_jobs(
    current_user: User = Depends(require_role(["company", "agency", "admin"])),
    db: Session = Depends(get_db)
):
    profile = company_service.get_by_user_id(db, current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company profile must be created first."
        )
    jobs = job_service.list_by_company(db, profile.id)
    return [
        JobResponse(
            id=j.id,
            company_id=j.company_id,
            company_name=profile.company_name,
            title=j.title,
            description=j.description,
            campaign_requirements=j.campaign_requirements,
            content_type=j.content_type,
            style=j.style,
            format=j.format,
            aspect_ratio=j.aspect_ratio,
            commercial_use=j.commercial_use,
            required_skills=j.required_skills,
            required_tools=j.required_tools,
            specialization=j.specialization,
            budget_range=j.budget_range,
            status=j.status,
            created_at=j.created_at,
            updated_at=j.updated_at
        )
        for j in jobs
    ]

@router.get("/{job_id}", response_model=JobResponse)
def get_job_by_id(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional)
):
    job = job_service.get_by_id(db, job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Creative brief / job not found."
        )

    # ── Role-based isolation: companies/agencies CANNOT view other companies' briefs ──
    if current_user and current_user.role in ["company", "agency"]:
        company_profile = company_service.get_by_user_id(db, current_user.id)
        if not company_profile or job.company_id != company_profile.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Commercial confidentiality restriction: Companies cannot view other companies' creative briefs."
            )

    return JobResponse(
        id=job.id,
        company_id=job.company_id,
        company_name=job.company.company_name if job.company else None,
        title=job.title,
        description=job.description,
        campaign_requirements=job.campaign_requirements,
        content_type=job.content_type,
        style=job.style,
        format=job.format,
        aspect_ratio=job.aspect_ratio,
        commercial_use=job.commercial_use,
        required_skills=job.required_skills,
        required_tools=job.required_tools,
        specialization=job.specialization,
        budget_range=job.budget_range,
        status=job.status,
        created_at=job.created_at,
        updated_at=job.updated_at
    )

@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(
    payload: JobCreate,
    current_user: User = Depends(require_role(["company", "agency", "admin"])),
    db: Session = Depends(get_db)
):
    profile = company_service.get_by_user_id(db, current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company profile must be created before publishing briefs."
        )
    job = job_service.create_job(db, profile.id, payload)
    return JobResponse(
        id=job.id,
        company_id=job.company_id,
        company_name=profile.company_name,
        title=job.title,
        description=job.description,
        campaign_requirements=job.campaign_requirements,
        content_type=job.content_type,
        style=job.style,
        format=job.format,
        aspect_ratio=job.aspect_ratio,
        commercial_use=job.commercial_use,
        required_skills=job.required_skills,
        required_tools=job.required_tools,
        specialization=job.specialization,
        budget_range=job.budget_range,
        status=job.status,
        created_at=job.created_at,
        updated_at=job.updated_at
    )

@router.put("/{job_id}", response_model=JobResponse)
def update_job(
    job_id: int,
    payload: JobUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    job = job_service.get_by_id(db, job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Creative brief / job not found."
        )
    # Server-side ownership check
    if job.company.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to modify this job."
        )
    updated = job_service.update_job(db, job, payload)
    return JobResponse(
        id=updated.id,
        company_id=updated.company_id,
        company_name=updated.company.company_name if updated.company else None,
        title=updated.title,
        description=updated.description,
        campaign_requirements=updated.campaign_requirements,
        content_type=updated.content_type,
        style=updated.style,
        format=updated.format,
        aspect_ratio=updated.aspect_ratio,
        commercial_use=updated.commercial_use,
        required_skills=updated.required_skills,
        required_tools=updated.required_tools,
        specialization=updated.specialization,
        budget_range=updated.budget_range,
        status=updated.status,
        created_at=updated.created_at,
        updated_at=updated.updated_at
    )

@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    job = job_service.get_by_id(db, job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Creative brief / job not found."
        )
    # Server-side ownership check
    if job.company.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this job."
        )
    job_service.delete_job(db, job)
    return None
