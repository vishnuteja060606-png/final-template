from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class ConnectionRequestCreate(BaseModel):
    receiver_id: int = Field(..., description="Target creator profile ID to connect with")

class ConnectionStatusUpdate(BaseModel):
    action: str = Field(..., pattern="^(accept|reject)$", description="Action: 'accept' or 'reject'")

class ConnectionResponse(BaseModel):
    id: int
    requester_id: int
    requester_name: str
    requester_avatar: Optional[str] = None
    requester_specialization: Optional[str] = None
    receiver_id: int
    receiver_name: str
    receiver_avatar: Optional[str] = None
    receiver_specialization: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CreatorConnectionsSummary(BaseModel):
    creator_id: int
    total_connections: int
    connections: list[ConnectionResponse] = []
