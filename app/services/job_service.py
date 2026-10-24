from sqlalchemy.orm import Session
from app.models.job import Job
from app.schemas.job import JobCreate, JobUpdate

class JobService:
    @staticmethod
    def get_by_id(db: Session, job_id: int) -> Job | None:
        return db.query(Job).filter(Job.id == job_id).first()

    @staticmethod
    def list_by_company(db: Session, company_id: int) -> list[Job]:
        return db.query(Job).filter(
            Job.company_id == company_id
        ).order_by(Job.created_at.desc()).all()

    @staticmethod
    def list_published(db: Session, limit: int = 50) -> list[Job]:
        return db.query(Job).filter(
            Job.status == "published"
        ).order_by(Job.created_at.desc()).limit(limit).all()

    @staticmethod
    def create_job(db: Session, company_id: int, data: JobCreate) -> Job:
        job = Job(
            company_id=company_id,
            title=data.title,
            description=data.description,
            campaign_requirements=data.campaign_requirements,
            content_type=data.content_type,
            style=data.style,
            format=data.format,
            aspect_ratio=data.aspect_ratio,
            commercial_use=data.commercial_use,
            required_skills=data.required_skills,
            required_tools=data.required_tools,
            specialization=data.specialization,
            budget_range=data.budget_range,
            status=data.status or "published"
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        return job

    @staticmethod
    def update_job(db: Session, job: Job, data: JobUpdate) -> Job:
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(job, field, value)
        db.commit()
        db.refresh(job)
        return job

    @staticmethod
    def delete_job(db: Session, job: Job) -> None:
        db.delete(job)
        db.commit()

job_service = JobService()
