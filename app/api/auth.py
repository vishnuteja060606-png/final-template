from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User
from app.models.creator import CreatorProfile
from app.models.company import CompanyProfile
from app.schemas.auth import UserRegister, UserLogin, Token, UserResponse
from app.services.auth_service import (
    AuthService,
    get_current_user,
    get_current_user_optional,
    require_role
)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

def require_creator(current_user: User = Depends(get_current_user)) -> User:
    """Role guardrail requiring authenticated creator."""
    if current_user.role != "creator":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Creator access required."
        )
    return current_user

def require_company(current_user: User = Depends(get_current_user)) -> User:
    """Role guardrail requiring authenticated company or agency."""
    if current_user.role not in ["company", "agency"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Company or agency access required."
        )
    return current_user

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, response: Response, db: Session = Depends(get_db)):
    email_clean = payload.email.lower().strip()

    # Check if user already exists
    existing = db.query(User).filter(User.email == email_clean).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email address already exists."
        )

    # Validate role
    role = payload.role.lower().strip()
    if role not in ["creator", "company", "agency"]:
        role = "creator"

    # Hash password & create user
    hashed = AuthService.hash_password(payload.password)
    new_user = User(
        email=email_clean,
        password_hash=hashed,
        role=role,
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Initialize corresponding profile
    profile_id = None
    if role == "creator":
        creator = CreatorProfile(
            user_id=new_user.id,
            display_name=payload.name.strip(),
            headline="AI Creator & Generative Artist",
            status="draft",
            hourly_rate_inr=1500,
            views_count=0
        )
        db.add(creator)
        db.commit()
        db.refresh(creator)
        profile_id = creator.id
    else:
        company = CompanyProfile(
            user_id=new_user.id,
            company_name=payload.name.strip(),
            industry="Media & Advertising",
            views_count=0
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
    email_clean = payload.email.lower().strip()
    user = db.query(User).filter(User.email == email_clean).first()
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

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(key="access_token")
    return {"message": "Successfully logged out."}

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/session")
def get_session(current_user: User | None = Depends(get_current_user_optional)):
    """Introspection endpoint for authentication status and role guardrails."""
    if not current_user:
        return {
            "authenticated": False,
            "user": None,
            "role": None,
            "profile_id": None
        }

    profile_id = None
    if current_user.role == "creator" and current_user.creator_profile:
        profile_id = current_user.creator_profile.id
    elif current_user.role in ["company", "agency"] and current_user.company_profile:
        profile_id = current_user.company_profile.id

    return {
        "authenticated": True,
        "user_id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
        "username": current_user.username,
        "profile_id": profile_id
    }
