from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class ReviewCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="Star rating from 1 to 5")
    project_title: str = Field(..., min_length=2, max_length=255, description="Campaign or project name")
    comment: str = Field(..., min_length=5, description="Detailed review feedback")
    tools_used: Optional[str] = Field(None, description="AI tools used during engagement")
    is_verified_engagement: bool = Field(False, description="Whether this review stems from an official verified contract")

class ReviewResponse(BaseModel):
    id: int
    creator_id: int
    company_id: int
    company_name: str
    company_logo: Optional[str] = None
    rating: int
    project_title: str
    comment: str
    tools_used: Optional[str] = None
    is_verified_engagement: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CreatorReviewsSummary(BaseModel):
    creator_id: int
    average_rating: float
    total_reviews: int
    reviews: list[ReviewResponse] = []
