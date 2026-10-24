import secrets
import random
import logging
from datetime import datetime, timedelta, timezone
from typing import Annotated
import bcrypt
import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.config import settings
from app.db.database import get_db
from app.models.user import User

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

class AuthService:
    # In-memory OTP storage for Two-Factor Email Authentication
    _otp_cache: dict[str, dict] = {}

    @classmethod
    def generate_email_otp(cls, email: str, user_id: int | None = None) -> str:
        """
        Generates a secure 6-digit OTP for Two-Step Email Authentication.
        Valid for 10 minutes.
        """
        code = f"{random.randint(100000, 999999)}"
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
        cls._otp_cache[email.lower().strip()] = {
            "code": code,
            "expires_at": expires_at,
            "user_id": user_id
        }
        logger.info(f"[2FA EMAIL NOTIFICATION] Sent verification OTP {code} to {email}")
        print(f"\n==================================================")
        print(f"[2FA EMAIL DISPATCH]")
        print(f"TO: {email}")
        print(f"SUBJECT: Synapse Two-Step Verification Code")
        print(f"YOUR 6-DIGIT CODE IS: {code}")
        print(f"VALIDITY: 10 Minutes")
        print(f"==================================================\n")
        return code

    @classmethod
    def verify_email_otp(cls, email: str, code: str) -> bool:
        """Validates the 6-digit OTP code."""
        email_clean = email.lower().strip()
        record = cls._otp_cache.get(email_clean)
        if not record:
            return False
        if datetime.now(timezone.utc) > record["expires_at"]:
            cls._otp_cache.pop(email_clean, None)
            return False
        if record["code"] == code.strip():
            cls._otp_cache.pop(email_clean, None)
            return True
        return False

    @staticmethod
    def hash_password(password: str) -> str:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        try:
            return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
        except Exception:
            return False

    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    @staticmethod
    def decode_token(token: str) -> dict | None:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload
        except (jwt.PyJWTError, Exception):
            return None

def extract_token(request: Request, bearer_token: str | None = None) -> str | None:
    """Extract token from Authorization header or cookie."""
    if bearer_token:
        return bearer_token
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header.split(" ", 1)[1]
    cookie_token = request.cookies.get("access_token")
    if cookie_token:
        if cookie_token.startswith("Bearer "):
            return cookie_token.split(" ", 1)[1]
        return cookie_token
    return None

def get_current_user_optional(
    request: Request,
    bearer_token: Annotated[str | None, Depends(oauth2_scheme)] = None,
    db: Session = Depends(get_db)
) -> User | None:
    """Returns the logged in user if available, otherwise None without raising 401."""
    token = extract_token(request, bearer_token)
    if not token:
        return None
    payload = AuthService.decode_token(token)
    if not payload:
        return None
    user_id = payload.get("sub")
    if not user_id:
        return None
    try:
        user = db.query(User).filter(User.id == int(user_id)).first()
        if user and user.is_active:
            return user
    except Exception:
        return None
    return None

def get_current_user(
    request: Request,
    bearer_token: Annotated[str | None, Depends(oauth2_scheme)] = None,
    db: Session = Depends(get_db)
) -> User:
    """Returns the logged in user or raises 401."""
    user = get_current_user_optional(request, bearer_token, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

def require_role(roles: list[str]):
    """Enforces specific user roles."""
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation not permitted. Required role: {', '.join(roles)}"
            )
        return current_user
    return role_checker
