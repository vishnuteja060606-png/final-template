from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class CompanyProfileBase(BaseModel):
    company_name: str = Field(..., min_length=2, max_length=255)
    industry: str | None = None
    description: str | None = None
    website: str | None = None
    location: str | None = None
    logo_url: str | None = None
    social_links: str | None = None  # JSON: {linkedin, twitter, website}
    tags: str | None = None

class CompanyProfileCreate(CompanyProfileBase):
    pass

class CompanyProfileUpdate(BaseModel):
    company_name: str | None = None
    industry: str | None = None
    description: str | None = None
    website: str | None = None
    location: str | None = None
    logo_url: str | None = None
    social_links: str | None = None
    tags: str | None = None

class CompanyProfileResponse(CompanyProfileBase):
    id: int
    user_id: int
    views_count: int = 0
    total_jobs_posted: int = 0
    total_reviews_given: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CompanyProfileCheckResponse(BaseModel):
    message: str
    company_id: int
    company_name: str
    views_count: int
    checked_by_creator: str | None = None
    checked_at: datetime

    model_config = ConfigDict(from_attributes=True)
