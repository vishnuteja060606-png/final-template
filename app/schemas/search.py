from pydantic import BaseModel, Field
from app.schemas.creator import CreatorProfileBrief
from app.schemas.job import JobResponse

class CreatorFilterParams(BaseModel):
    query: str | None = None
    skill: str | None = None
    specialization: str | None = None
    tool: str | None = None
    content_type: str | None = None
    aspect_ratio: str | None = None
    format: str | None = None
    tag: str | None = None
    page: int = Field(1, ge=1)
    limit: int = Field(20, ge=1, le=100)

class CreatorSearchResult(BaseModel):
    items: list[CreatorProfileBrief]
    total: int
    page: int
    limit: int
    active_filters: dict[str, str | None] = {}
    message: str | None = None

class JobFilterParams(BaseModel):
    query: str | None = None
    content_type: str | None = None
    specialization: str | None = None
    skill: str | None = None
    tool: str | None = None
    status: str | None = "published"
    page: int = Field(1, ge=1)
    limit: int = Field(20, ge=1, le=100)

class JobSearchResult(BaseModel):
    items: list[JobResponse]
    total: int
    page: int
    limit: int
    active_filters: dict[str, str | None] = {}
    message: str | None = None
