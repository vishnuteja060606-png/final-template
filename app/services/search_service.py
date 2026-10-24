from sqlalchemy import or_, and_, func
from sqlalchemy.orm import Session, joinedload
from app.models.creator import CreatorProfile
from app.models.portfolio import PortfolioItem
from app.models.job import Job
from app.schemas.search import CreatorFilterParams, CreatorSearchResult, JobFilterParams, JobSearchResult
from app.schemas.creator import CreatorProfileBrief, VerificationSignalResponse
from app.schemas.job import JobResponse

class SearchService:
    @staticmethod
    def search_creators(db: Session, params: CreatorFilterParams) -> CreatorSearchResult:
        # Base query with joined relationships for performance
        query = db.query(CreatorProfile).options(
            joinedload(CreatorProfile.portfolio_items),
            joinedload(CreatorProfile.verification_signals)
        )

        active_filters = {}

        # 1. Text Query Filter
        if params.query and params.query.strip():
            clean_q = params.query.strip().lower()
            pattern = f"%{clean_q}%"
            active_filters["query"] = params.query.strip()

            # Matches creator profile or any of their portfolio items
            creator_match = or_(
                func.lower(CreatorProfile.display_name).like(pattern),
                func.lower(CreatorProfile.headline).like(pattern),
                func.lower(CreatorProfile.bio).like(pattern),
                func.lower(CreatorProfile.skills).like(pattern),
                func.lower(CreatorProfile.tools_models).like(pattern),
                func.lower(CreatorProfile.specialization).like(pattern),
                func.lower(CreatorProfile.workflow).like(pattern),
            )
            # Portfolio item match subquery
            portfolio_match = CreatorProfile.id.in_(
                db.query(PortfolioItem.creator_id).filter(
                    or_(
                        func.lower(PortfolioItem.title).like(pattern),
                        func.lower(PortfolioItem.description).like(pattern),
                        func.lower(PortfolioItem.tools_models).like(pattern),
                        func.lower(PortfolioItem.skills).like(pattern),
                        func.lower(PortfolioItem.tags).like(pattern),
                    )
                )
            )
            query = query.filter(or_(creator_match, portfolio_match))

        # 2. Skill Filter
        if params.skill and params.skill.strip():
            clean_skill = params.skill.strip().lower()
            pattern = f"%{clean_skill}%"
            active_filters["skill"] = params.skill.strip()
            
            creator_skill_match = func.lower(CreatorProfile.skills).like(pattern)
            portfolio_skill_match = CreatorProfile.id.in_(
                db.query(PortfolioItem.creator_id).filter(func.lower(PortfolioItem.skills).like(pattern))
            )
            query = query.filter(or_(creator_skill_match, portfolio_skill_match))

        # 3. Tool / Model Filter
        if params.tool and params.tool.strip():
            clean_tool = params.tool.strip().lower()
            pattern = f"%{clean_tool}%"
            active_filters["tool"] = params.tool.strip()

            creator_tool_match = func.lower(CreatorProfile.tools_models).like(pattern)
            portfolio_tool_match = CreatorProfile.id.in_(
                db.query(PortfolioItem.creator_id).filter(func.lower(PortfolioItem.tools_models).like(pattern))
            )
            query = query.filter(or_(creator_tool_match, portfolio_tool_match))

        # 4. Specialization Filter
        if params.specialization and params.specialization.strip():
            clean_spec = params.specialization.strip().lower()
            pattern = f"%{clean_spec}%"
            active_filters["specialization"] = params.specialization.strip()

            creator_spec_match = func.lower(CreatorProfile.specialization).like(pattern)
            portfolio_spec_match = CreatorProfile.id.in_(
                db.query(PortfolioItem.creator_id).filter(func.lower(PortfolioItem.specialization).like(pattern))
            )
            query = query.filter(or_(creator_spec_match, portfolio_spec_match))

        # 5. Content Type Filter (e.g. Video, Animation, Image)
        if params.content_type and params.content_type.strip():
            clean_ct = params.content_type.strip().lower()
            pattern = f"%{clean_ct}%"
            active_filters["content_type"] = params.content_type.strip()

            query = query.filter(
                CreatorProfile.id.in_(
                    db.query(PortfolioItem.creator_id).filter(func.lower(PortfolioItem.content_type).like(pattern))
                )
            )

        # 6. Aspect Ratio Filter (e.g. 16:9, 9:16)
        if params.aspect_ratio and params.aspect_ratio.strip():
            clean_ar = params.aspect_ratio.strip().lower()
            pattern = f"%{clean_ar}%"
            active_filters["aspect_ratio"] = params.aspect_ratio.strip()

            query = query.filter(
                CreatorProfile.id.in_(
                    db.query(PortfolioItem.creator_id).filter(func.lower(PortfolioItem.aspect_ratio).like(pattern))
                )
            )

        # 7. Format Filter (e.g. MP4, PNG)
        if params.format and params.format.strip():
            clean_fmt = params.format.strip().lower()
            pattern = f"%{clean_fmt}%"
            active_filters["format"] = params.format.strip()

            query = query.filter(
                CreatorProfile.id.in_(
                    db.query(PortfolioItem.creator_id).filter(func.lower(PortfolioItem.format).like(pattern))
                )
            )

        # 8. Tag Filter
        if params.tag and params.tag.strip():
            clean_tag = params.tag.strip().lower()
            pattern = f"%{clean_tag}%"
            active_filters["tag"] = params.tag.strip()

            query = query.filter(
                CreatorProfile.id.in_(
                    db.query(PortfolioItem.creator_id).filter(func.lower(PortfolioItem.tags).like(pattern))
                )
            )

        # Count total matches before pagination
        total = query.count()

        # Sort: verified first, then newest
        query = query.order_by(CreatorProfile.is_verified.desc(), CreatorProfile.created_at.desc())

        # Pagination
        offset = (params.page - 1) * params.limit
        results = query.offset(offset).limit(params.limit).all()

        brief_items = [
            CreatorProfileBrief(
                id=c.id,
                user_id=c.user_id,
                display_name=c.display_name,
                headline=c.headline,
                specialization=c.specialization,
                skills=c.skills,
                tools_models=c.tools_models,
                location=c.location,
                profile_image_url=c.profile_image_url,
                is_verified=c.is_verified,
                portfolio_count=len(c.portfolio_items),
                verification_signals=[
                    VerificationSignalResponse.model_validate(sig) for sig in c.verification_signals
                ]
            )
            for c in results
        ]

        message = None
        if total == 0:
            message = "No creators found matching your criteria. Try adjusting or clearing your filters."

        return CreatorSearchResult(
            items=brief_items,
            total=total,
            page=params.page,
            limit=params.limit,
            active_filters=active_filters,
            message=message
        )

    @staticmethod
    def search_jobs(db: Session, params: JobFilterParams) -> JobSearchResult:
        query = db.query(Job).options(joinedload(Job.company))
        active_filters = {}

        if params.status:
            query = query.filter(Job.status == params.status)
            active_filters["status"] = params.status

        if params.query and params.query.strip():
            clean_q = params.query.strip().lower()
            pattern = f"%{clean_q}%"
            active_filters["query"] = params.query.strip()
            query = query.filter(
                or_(
                    func.lower(Job.title).like(pattern),
                    func.lower(Job.description).like(pattern),
                    func.lower(Job.campaign_requirements).like(pattern),
                    func.lower(Job.required_skills).like(pattern),
                    func.lower(Job.required_tools).like(pattern),
                )
            )

        if params.content_type and params.content_type.strip():
            pattern = f"%{params.content_type.strip().lower()}%"
            active_filters["content_type"] = params.content_type.strip()
            query = query.filter(func.lower(Job.content_type).like(pattern))

        if params.specialization and params.specialization.strip():
            pattern = f"%{params.specialization.strip().lower()}%"
            active_filters["specialization"] = params.specialization.strip()
            query = query.filter(func.lower(Job.specialization).like(pattern))

        if params.skill and params.skill.strip():
            pattern = f"%{params.skill.strip().lower()}%"
            active_filters["skill"] = params.skill.strip()
            query = query.filter(func.lower(Job.required_skills).like(pattern))

        if params.tool and params.tool.strip():
            pattern = f"%{params.tool.strip().lower()}%"
            active_filters["tool"] = params.tool.strip()
            query = query.filter(func.lower(Job.required_tools).like(pattern))

        total = query.count()
        query = query.order_by(Job.created_at.desc())

        offset = (params.page - 1) * params.limit
        results = query.offset(offset).limit(params.limit).all()

        job_responses = [
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
            for j in results
        ]

        message = None
        if total == 0:
            message = "No projects found matching your search. Try adjusting your filters."

        return JobSearchResult(
            items=job_responses,
            total=total,
            page=params.page,
            limit=params.limit,
            active_filters=active_filters,
            message=message
        )

search_service = SearchService()
