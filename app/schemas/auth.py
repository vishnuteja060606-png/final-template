from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, description="Password must be at least 6 characters")
    role: str = Field("creator", description="Role: 'creator' or 'company'")
    name: str = Field(..., min_length=2, description="Display name or company name")

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: int
    profile_id: int | None = None

class TokenData(BaseModel):
    email: str | None = None
    user_id: int | None = None
    role: str | None = None

class UserResponse(BaseModel):
    id: int
    email: str
    role: str
    is_active: bool
    is_2fa_enabled: bool = True
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Two-Factor Email Authentication Schemas
class OTPRequest(BaseModel):
    email: EmailStr

class OTPVerify(BaseModel):
    email: EmailStr
    code: str = Field(..., min_length=6, max_length=6, description="6-digit verification code")

class OTPResponse(BaseModel):
    message: str
    email: str
    expires_in_minutes: int = 10
