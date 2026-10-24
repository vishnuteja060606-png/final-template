from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class JobBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    campaign_requirements: str | None = None
    content_type: str | None = Field(None, description="Video, Animation, Image, Graphic")
    style: str | None = None
    format: str | None = None
    aspect_ratio: str | None = None
    commercial_use: str | None = "Full Commercial Buyout"
    required_skills: str | None = None  # Comma-separated
    required_tools: str | None = None  # Comma-separated
    specialization: str | None = None
    budget_range: str | None = None
    budget_inr: int = 50000  # Primary currency in INR (₹)
    status: str = "published"  # draft, published, closed, archived

    def skills_list(self) -> list[str]:
        if not self.required_skills:
            return []
        return [s.strip() for s in self.required_skills.split(",") if s.strip()]

    def tools_list(self) -> list[str]:
        if not self.required_tools:
            return []
        return [t.strip() for t in self.required_tools.split(",") if t.strip()]

class JobCreate(JobBase):
    pass

class JobUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    campaign_requirements: str | None = None
    content_type: str | None = None
    style: str | None = None
    format: str | None = None
    aspect_ratio: str | None = None
    commercial_use: str | None = None
    required_skills: str | None = None
    required_tools: str | None = None
    specialization: str | None = None
    budget_range: str | None = None
    budget_inr: int | None = None
    status: str | None = None

class JobResponse(JobBase):
    id: int
    company_id: int
    company_name: str | None = None
    budget_usd: int = 588
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
