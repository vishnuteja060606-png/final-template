from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.config import settings, BASE_DIR
from app.db.database import get_db, init_db
from app.db.seed import seed_database
from app.models.user import User
from app.models.creator import CreatorProfile
from app.services.auth_service import get_current_user_optional, require_role
from app.services.creator_service import creator_service
from app.services.company_service import company_service
from app.services.job_service import job_service
from app.services.portfolio_service import portfolio_service
from app.services.engagement_service import engagement_service
from app.services.search_service import search_service
from app.services.review_service import review_service
from app.services.connection_service import connection_service
from app.schemas.search import CreatorFilterParams, JobFilterParams

# Import API routers
from app.api.auth import router as auth_router
from app.api.creators import router as creators_router
from app.api.portfolios import router as portfolios_router
from app.api.companies import router as companies_router
from app.api.jobs import router as jobs_router
from app.api.search import router as search_router
from app.api.engagements import router as engagements_router
from app.api.ai import router as ai_router
from app.api.advanced import router as advanced_router
from app.api.reviews import router as reviews_router
from app.api.connections import router as connections_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure database tables exist and seed demo data if empty
    init_db()
    seed_database()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI Content Creator Marketplace linking brands and creative agencies with AI-native creators.",
    version="2.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static & Upload Files Mount
static_dir = BASE_DIR / "app" / "static"
upload_dir = Path(settings.UPLOAD_DIR).resolve()
upload_dir.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
app.mount("/uploads", StaticFiles(directory=str(upload_dir)), name="uploads")

# Templates Configuration
templates_dir = BASE_DIR / "app" / "templates"
templates = Jinja2Templates(directory=str(templates_dir))

# Include API Routers
app.include_router(auth_router)
app.include_router(creators_router)
app.include_router(portfolios_router)
app.include_router(companies_router)
app.include_router(jobs_router)
app.include_router(search_router)
app.include_router(engagements_router)
app.include_router(ai_router)
app.include_router(advanced_router)
app.include_router(reviews_router)
app.include_router(connections_router)

# Healthcheck
@app.get("/health", tags=["System"])
def healthcheck():
    return {
        "status": "healthy",
        "app": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
        "primary_currency": settings.PRIMARY_CURRENCY
    }

# Web View Routes (HTML Server-Rendered)
@app.get("/", response_class=HTMLResponse, tags=["Web Views"])
def homepage(request: Request, db: Session = Depends(get_db), current_user: User | None = Depends(get_current_user_optional)):
    featured_creators = creator_service.list_featured(db, limit=4)
    featured_jobs = job_service.list_published(db, limit=3)
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "current_user": current_user,
            "featured_creators": featured_creators,
            "featured_jobs": featured_jobs,
            "active_page": "home"
        }
    )

@app.get("/login", response_class=HTMLResponse, tags=["Web Views"])
def login_page(request: Request, current_user: User | None = Depends(get_current_user_optional)):
    if current_user:
        if current_user.role == "creator":
            return RedirectResponse(url="/dashboard/creator")
        return RedirectResponse(url="/dashboard/company")
    return templates.TemplateResponse(request=request, name="auth/login.html", context={"current_user": None, "active_page": "auth"})

@app.get("/register", response_class=HTMLResponse, tags=["Web Views"])
def register_page(request: Request, current_user: User | None = Depends(get_current_user_optional)):
    if current_user:
        if current_user.role == "creator":
            return RedirectResponse(url="/dashboard/creator")
        return RedirectResponse(url="/dashboard/company")
    return templates.TemplateResponse(request=request, name="auth/register.html", context={"current_user": None, "active_page": "auth"})

@app.get("/verify-otp", response_class=HTMLResponse, tags=["Web Views"])
def verify_otp_page(request: Request, email: str | None = None, current_user: User | None = Depends(get_current_user_optional)):
    return templates.TemplateResponse(
        request=request,
        name="auth/verify_otp.html",
        context={"request": request, "current_user": current_user, "email": email or "", "active_page": "auth"}
    )

@app.get("/creators", response_class=HTMLResponse, tags=["Web Views"])
def creators_discovery_page(
    request: Request,
    query: str | None = Query(None),
    skill: str | None = Query(None),
    specialization: str | None = Query(None),
    tool: str | None = Query(None),
    content_type: str | None = Query(None),
    aspect_ratio: str | None = Query(None),
    format: str | None = Query(None),
    tag: str | None = Query(None),
    search_mode: str | None = Query("deterministic"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional)
):
    # Rule: Creator should not able to see other creators
    if current_user and current_user.role == "creator":
        return RedirectResponse(url="/projects?notice=creators_restricted", status_code=303)

    if search_mode == "semantic" and query and query.strip():
        from app.services.advanced_container import container
        sem_results = container.embedding_service.search_similar(query=query, entity_type="creator", top_k=limit, db=db)
        found_ids = [r["entity_id"] for r in sem_results]
        creators = db.query(CreatorProfile).filter(CreatorProfile.id.in_(found_ids)).all() if found_ids else []
        score_map = {r["entity_id"]: r["similarity_score"] for r in sem_results}
        for c in creators:
            c.semantic_score = round(score_map.get(c.id, 0.0) * 100, 1)
        creators.sort(key=lambda c: getattr(c, "semantic_score", 0.0), reverse=True)
        items = creators
        total = len(creators)
        active_filters = {"query": query, "search_mode": "semantic"}
        message = f"Found {total} creators via AI Semantic Search for '{query}'"
    elif search_mode == "hybrid" and query and query.strip():
        from app.services.advanced_container import container
        sem_results = container.embedding_service.search_similar(query=query, entity_type="creator", top_k=limit, db=db)
        vector_ids = [r["entity_id"] for r in sem_results]
        q_like = f"%{query.strip().lower()}%"
        kw_creators = db.query(CreatorProfile.id).filter(
            (CreatorProfile.display_name.ilike(q_like)) |
            (CreatorProfile.skills.ilike(q_like)) |
            (CreatorProfile.tools_models.ilike(q_like)) |
            (CreatorProfile.specialization.ilike(q_like)) |
            (CreatorProfile.bio.ilike(q_like))
        ).limit(limit).all()
        keyword_ids = [c[0] for c in kw_creators]
        fused = container.ranking_service.reciprocal_rank_fusion(keyword_ids, vector_ids)
        fused_map = {cid: score for cid, score in fused}
        creators = db.query(CreatorProfile).filter(CreatorProfile.id.in_(list(fused_map.keys()))).all() if fused_map else []
        for c in creators:
            c.rrf_score = round(fused_map.get(c.id, 0.0), 4)
        creators.sort(key=lambda c: getattr(c, "rrf_score", 0.0), reverse=True)
        items = creators
        total = len(creators)
        active_filters = {"query": query, "search_mode": "hybrid"}
        message = f"Retrieved {total} creators via Hybrid Search (Reciprocal Rank Fusion)"
    else:
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
        result = search_service.search_creators(db, params)
        items = result.items
        total = result.total
        active_filters = result.active_filters
        message = result.message

    return templates.TemplateResponse(
        request=request,
        name="creators/list.html",
        context={
            "current_user": current_user,
            "items": items,
            "total": total,
            "active_filters": active_filters,
            "message": message,
            "search_mode": search_mode,
            "active_page": "creators"
        }
    )

@app.get("/creators/{creator_id}", response_class=HTMLResponse, tags=["Web Views"])
def creator_detail_page(
    creator_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional)
):
    # Rule: Creator should not able to see other creators
    if current_user and current_user.role == "creator" and current_user.creator_profile and current_user.creator_profile.id != creator_id:
        return RedirectResponse(url="/dashboard/creator?notice=creators_restricted", status_code=303)

    creator = creator_service.get_by_id(db, creator_id)
    if not creator:
        raise HTTPException(status_code=404, detail="Creator profile not found.")
    
    # Increment view counter
    creator_service.increment_view(db, creator_id)

    # Check connection status if visitor is a logged-in creator
    connection_status = "none"
    if current_user and current_user.role == "creator" and current_user.creator_profile:
        connection_status = connection_service.check_connection_status(db, current_user.creator_profile.id, creator.id)

    reviews_summary = review_service.get_reviews_for_creator(db, creator_id)
    connections_summary = connection_service.get_creator_connections(db, creator_id)

    return templates.TemplateResponse(
        request=request,
        name="creators/detail.html",
        context={
            "current_user": current_user,
            "creator": creator,
            "reviews_summary": reviews_summary,
            "connections_summary": connections_summary,
            "connection_status": connection_status,
            "active_page": "creators"
        }
    )

@app.get("/projects", response_class=HTMLResponse, tags=["Web Views"])
def projects_discovery_page(
    request: Request,
    query: str | None = Query(None),
    content_type: str | None = Query(None),
    specialization: str | None = Query(None),
    skill: str | None = Query(None),
    tool: str | None = Query(None),
    status: str | None = Query("published"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional)
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
    result = search_service.search_jobs(db, params)
    return templates.TemplateResponse(
        request=request,
        name="jobs/list.html",
        context={
            "current_user": current_user,
            "items": result.items,
            "total": result.total,
            "active_filters": result.active_filters,
            "message": result.message,
            "active_page": "projects"
        }
    )

@app.get("/projects/{job_id}", response_class=HTMLResponse, tags=["Web Views"])
def project_detail_page(
    job_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional)
):
    job = job_service.get_by_id(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Creative brief not found.")
    return templates.TemplateResponse(
        request=request,
        name="jobs/detail.html",
        context={
            "current_user": current_user,
            "job": job,
            "active_page": "projects"
        }
    )

@app.get("/companies", response_class=HTMLResponse, tags=["Web Views"])
def companies_directory_page(
    request: Request,
    query: str | None = Query(None),
    industry: str | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional)
):
    # Rule: Companies should not see other companies
    if current_user and current_user.role in ["company", "agency"]:
        return RedirectResponse(url="/creators?notice=companies_restricted", status_code=303)

    companies = company_service.list_companies(db, query=query, industry=industry)
    return templates.TemplateResponse(
        request=request,
        name="companies/list.html",
        context={
            "request": request,
            "current_user": current_user,
            "companies": companies,
            "query": query or "",
            "industry": industry or "",
            "active_page": "companies"
        }
    )

@app.get("/companies/{company_id}", response_class=HTMLResponse, tags=["Web Views"])
def company_detail_page(
    company_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional)
):
    # Rule: Companies should not see other companies
    if current_user and current_user.role in ["company", "agency"] and current_user.company_profile and current_user.company_profile.id != company_id:
        return RedirectResponse(url="/dashboard/company?notice=companies_restricted", status_code=303)

    company, _ = company_service.record_company_profile_check(db, company_id, current_user)
    recent_checks = company_service.get_recent_creator_checks_for_company(db, company_id, limit=5)
    return templates.TemplateResponse(
        request=request,
        name="companies/detail.html",
        context={
            "request": request,
            "current_user": current_user,
            "company": company,
            "recent_checks": recent_checks,
            "active_page": "companies"
        }
    )

@app.get("/dashboard", tags=["Web Views"])
def dashboard_redirect(current_user: User = Depends(get_current_user_optional)):
    if not current_user:
        return RedirectResponse(url="/login")
    if current_user.role == "creator":
        return RedirectResponse(url="/dashboard/creator")
    return RedirectResponse(url="/dashboard/company")

@app.get("/dashboard/creator", response_class=HTMLResponse, tags=["Web Views"])
def creator_dashboard_view(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["creator", "admin"]))
):
    profile = creator_service.get_by_user_id(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Creator profile not found.")
    
    # Auto-refresh publication status (2 uploads rule)
    creator_service.refresh_publication_status(db, profile.id)
    
    portfolio_items = portfolio_service.list_by_creator(db, profile.id)
    engagements = engagement_service.list_for_creator(db, profile.id)
    completeness = creator_service.calculate_completeness(profile)
    checked_companies = company_service.get_companies_checked_by_creator(db, profile.id, limit=6)
    reviews_summary = review_service.get_reviews_for_creator(db, profile.id)
    connections_summary = connection_service.get_creator_connections(db, profile.id)

    return templates.TemplateResponse(
        request=request,
        name="dashboard/creator.html",
        context={
            "current_user": current_user,
            "profile": profile,
            "portfolio_items": portfolio_items,
            "engagements": engagements,
            "completeness": completeness,
            "checked_companies": checked_companies,
            "reviews_summary": reviews_summary,
            "connections_summary": connections_summary,
            "active_page": "dashboard"
        }
    )

@app.get("/dashboard/company", response_class=HTMLResponse, tags=["Web Views"])
def company_dashboard_view(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["company", "agency", "admin"]))
):
    profile = company_service.get_by_user_id(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Company profile not found.")
    jobs = job_service.list_by_company(db, profile.id)
    engagements = engagement_service.list_for_company(db, profile.id)
    recent_creator_checks = company_service.get_recent_creator_checks_for_company(db, profile.id, limit=8)

    return templates.TemplateResponse(
        request=request,
        name="dashboard/company.html",
        context={
            "current_user": current_user,
            "profile": profile,
            "jobs": jobs,
            "engagements": engagements,
            "recent_creator_checks": recent_creator_checks,
            "active_page": "dashboard"
        }
    )

@app.get("/ai-builder", response_class=HTMLResponse, tags=["Web Views"])
def ai_builder_page(request: Request, current_user: User | None = Depends(get_current_user_optional)):
    return templates.TemplateResponse(
        request=request,
        name="ai/brief_builder.html",
        context={
            "current_user": current_user,
            "active_page": "ai_builder"
        }
    )
