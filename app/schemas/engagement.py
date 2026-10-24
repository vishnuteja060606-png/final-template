from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class EngagementCreate(BaseModel):
    creator_id: int
    job_id: int | None = None
    message: str = Field(..., min_length=1, description="Message or project proposal to the creator")
    proposed_budget: str | None = None
    bid_amount_inr: int | None = Field(None, description="Initial monetary price bid in INR (₹)")

class EngagementUpdate(BaseModel):
    status: str = Field(..., description="pending, accepted, declined, completed, negotiating")

class CounterOfferRequest(BaseModel):
    counter_offer_inr: int = Field(..., gt=0, description="Counter-offer price in INR (₹)")
    notes: str | None = Field(None, description="Terms or revision notes for negotiation")

class EngagementResponse(BaseModel):
    id: int
    company_id: int
    creator_id: int
    job_id: int | None = None
    status: str
    message: str
    proposed_budget: str | None = None
    bid_amount_inr: int | None = None
    counter_offer_inr: int | None = None
    negotiation_status: str | None = "initial_bid"
    negotiation_notes: str | None = None
    last_negotiated_by: str | None = None
    active_price_inr: int = 0
    created_at: datetime
    updated_at: datetime
    company_name: str | None = None
    creator_name: str | None = None
    job_title: str | None = None

    model_config = ConfigDict(from_attributes=True)
