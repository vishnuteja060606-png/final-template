from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class PortfolioItemBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    description: str | None = None
    content_type: str = Field(..., description="Video, Animation, Image, Graphic, 3D, Audio")
    aspect_ratio: str | None = Field(None, description="16:9, 9:16, 1:1, 4:5, 21:9")
    format: str | None = Field(None, description="MP4, PNG, JPG, WebM")
    tools_models: str | None = Field(None, description="Comma-separated AI tools/models used")
    skills: str | None = Field(None, description="Comma-separated skills used")
    specialization: str | None = None
    tags: str | None = None
    workflow: str | None = None

class PortfolioItemCreate(PortfolioItemBase):
    pass

class PortfolioItemUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    content_type: str | None = None
    aspect_ratio: str | None = None
    format: str | None = None
    tools_models: str | None = None
    skills: str | None = None
    specialization: str | None = None
    tags: str | None = None
    workflow: str | None = None

class PortfolioPinToggleRequest(BaseModel):
    is_pinned: bool = Field(..., description="Whether to pin (True) or unpin (False) this work")

class PortfolioItemResponse(PortfolioItemBase):
    id: int
    creator_id: int
    file_path: str
    original_filename: str
    mime_type: str
    file_size: int
    is_pinned: bool = False
    pin_order: int = 0
    views_count: int = 0
    
    # Moderation & Approved Works Status
    is_approved: bool = True
    approval_status: str = "approved"
    moderation_note: str | None = None

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
