from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class EngagementCreate(BaseModel):
    creator_id: int
    job_id: int | None = None
    message: str = Field(..., min_length=1, description="Message or project proposal to the creator")
    proposed_budget: str | None = None

class EngagementUpdate(BaseModel):
    status: str = Field(..., description="pending, accepted, declined, completed")

class EngagementResponse(BaseModel):
    id: int
    company_id: int
    creator_id: int
    job_id: int | None = None
    status: str
    message: str
    proposed_budget: str | None = None
    created_at: datetime
    updated_at: datetime
    company_name: str | None = None
    creator_name: str | None = None
    job_title: str | None = None

    model_config = ConfigDict(from_attributes=True)
