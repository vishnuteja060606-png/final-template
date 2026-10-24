from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User
from app.models.creator import CreatorProfile
from app.models.company import CompanyProfile
from app.schemas.auth import (
    UserRegister, UserLogin, Token, UserResponse,
    OTPRequest, OTPVerify, OTPResponse
)
from app.services.auth_service import AuthService, get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, response: Response, db: Session = Depends(get_db)):
    # Check if user already exists
    existing = db.query(User).filter(User.email == payload.email.lower()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email address already exists."
        )

    # Validate role
    role = payload.role.lower()
    if role not in ["creator", "company", "agency"]:
        role = "creator"

    # Hash password & create user
    hashed = AuthService.hash_password(payload.password)
    new_user = User(
        email=payload.email.lower(),
        password_hash=hashed,
        role=role,
        is_active=True,
        is_2fa_enabled=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Initialize corresponding profile
    profile_id = None
    if role == "creator":
        creator = CreatorProfile(
            user_id=new_user.id,
            display_name=payload.name,
            headline="AI Creator & Generative Artist"
        )
        db.add(creator)
        db.commit()
        db.refresh(creator)
        profile_id = creator.id
    else:
        company = CompanyProfile(
            user_id=new_user.id,
            company_name=payload.name,
            industry="Media & Advertising"
        )
        db.add(company)
        db.commit()
        db.refresh(company)
        profile_id = company.id

    # Create JWT access token
    token = AuthService.create_access_token(
        data={"sub": str(new_user.id), "role": new_user.role, "email": new_user.email}
    )

    # Set secure HTTP-only cookie for web browser navigation
    response.set_cookie(
        key="access_token",
        value=f"Bearer {token}",
        httponly=True,
        max_age=86400,
        samesite="lax"
    )

    return Token(
        access_token=token,
        token_type="bearer",
        role=new_user.role,
        user_id=new_user.id,
        profile_id=profile_id
    )

@router.post("/login", response_model=Token)
def login(payload: UserLogin, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if not user or not AuthService.verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled."
        )

    profile_id = None
    if user.creator_profile:
        profile_id = user.creator_profile.id
    elif user.company_profile:
        profile_id = user.company_profile.id

    token = AuthService.create_access_token(
        data={"sub": str(user.id), "role": user.role, "email": user.email}
    )

    response.set_cookie(
        key="access_token",
        value=f"Bearer {token}",
        httponly=True,
        max_age=86400,
        samesite="lax"
    )

    return Token(
        access_token=token,
        token_type="bearer",
        role=user.role,
        user_id=user.id,
        profile_id=profile_id
    )

# ========================================================
# Two-Step Authentication via Email (2FA / OTP)
# ========================================================
@router.post("/send-otp", response_model=OTPResponse)
def send_email_otp(payload: OTPRequest, db: Session = Depends(get_db)):
    """
    Two-Step Authentication: Dispatches a 6-digit verification code to the user's email.
    """
    user = db.query(User).filter(User.email == payload.email.lower().strip()).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No account found with this email address."
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account is deactivated."
        )

    code = AuthService.generate_email_otp(user.email, user.id)
    user.email_otp_code = code
    db.commit()
    return OTPResponse(
        message=f"Two-step verification code sent to {user.email}.",
        email=user.email,
        expires_in_minutes=10
    )

@router.post("/verify-otp", response_model=Token)
def verify_email_otp(payload: OTPVerify, response: Response, db: Session = Depends(get_db)):
    """
    Two-Step Authentication: Verifies the 6-digit email OTP and issues authenticated session.
    """
    is_valid = AuthService.verify_email_otp(payload.email, payload.code)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification code. Please request a new code."
        )

    user = db.query(User).filter(User.email == payload.email.lower().strip()).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    profile_id = None
    if user.creator_profile:
        profile_id = user.creator_profile.id
    elif user.company_profile:
        profile_id = user.company_profile.id

    token = AuthService.create_access_token(
        data={"sub": str(user.id), "role": user.role, "email": user.email}
    )

    response.set_cookie(
        key="access_token",
        value=f"Bearer {token}",
        httponly=True,
        max_age=86400,
        samesite="lax"
    )

    return Token(
        access_token=token,
        token_type="bearer",
        role=user.role,
        user_id=user.id,
        profile_id=profile_id
    )

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(key="access_token")
    return {"message": "Successfully logged out."}

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
