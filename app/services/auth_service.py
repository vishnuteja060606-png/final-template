import secrets
import random
import logging
import smtplib
import threading
from datetime import datetime, timedelta, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
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


def _send_otp_email_smtp(email: str, code: str) -> None:
    """
    Sends the 6-digit OTP via SMTP in a background thread.
    Falls back gracefully to console print if SMTP is not configured.
    """
    if not settings.SMTP_USER.strip() or not settings.SMTP_PASSWORD.strip():
        # Graceful fallback — no SMTP configured
        print(f"\n==================================================")
        print(f"[2FA EMAIL DISPATCH — Console Fallback]")
        print(f"TO      : {email}")
        print(f"SUBJECT : Synapse Two-Step Verification Code")
        print(f"OTP CODE: {code}")
        print(f"VALID   : 10 Minutes")
        print(f"==================================================\n")
        return

    try:
        html_body = f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Synapse — Verification Code</title>
</head>
<body style="margin:0;padding:0;background:#0f172a;font-family:'Segoe UI',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#0f172a;padding:40px 0;">
    <tr>
      <td align="center">
        <table width="520" cellpadding="0" cellspacing="0" style="background:#1e293b;border-radius:16px;overflow:hidden;border:1px solid rgba(99,102,241,0.3);">
          <!-- Header -->
          <tr>
            <td style="background:linear-gradient(135deg,#4f46e5,#7c3aed);padding:32px;text-align:center;">
              <div style="font-size:36px;margin-bottom:8px;">🛡️</div>
              <h1 style="color:#fff;font-size:22px;margin:0;font-weight:700;letter-spacing:-0.5px;">
                Synapse Marketplace
              </h1>
              <p style="color:rgba(255,255,255,0.8);font-size:13px;margin:6px 0 0;">
                Two-Step Verification
              </p>
            </td>
          </tr>
          <!-- Body -->
          <tr>
            <td style="padding:36px 40px;text-align:center;">
              <p style="color:#94a3b8;font-size:15px;margin:0 0 24px;">
                Your secure 6-digit verification code is:
              </p>

              <!-- OTP Code Box -->
              <div style="background:#0f172a;border:2px solid #4f46e5;border-radius:12px;padding:24px 40px;display:inline-block;margin-bottom:24px;">
                <span style="font-size:48px;font-weight:900;letter-spacing:12px;color:#818cf8;font-family:'Courier New',monospace;">
                  {code}
                </span>
              </div>

              <p style="color:#64748b;font-size:13px;margin:0 0 8px;">
                ⏱️ This code expires in <strong style="color:#f59e0b;">10 minutes</strong>.
              </p>
              <p style="color:#64748b;font-size:12px;margin:0;">
                If you did not request this code, please ignore this email.<br>
                Your account remains secure.
              </p>
            </td>
          </tr>
          <!-- Footer -->
          <tr>
            <td style="background:#0f172a;padding:20px 40px;text-align:center;border-top:1px solid rgba(255,255,255,0.07);">
              <p style="color:#475569;font-size:12px;margin:0;">
                © 2024 Synapse AI Creator Marketplace. All rights reserved.<br>
                This is an automated security email — please do not reply.
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"🔐 Synapse — Your Verification Code: {code}"
        msg["From"] = settings.SMTP_FROM
        msg["To"] = email

        # Plain-text fallback
        plain_text = (
            f"Your Synapse 2FA verification code is: {code}\n"
            f"This code expires in 10 minutes.\n\n"
            f"If you did not request this, please ignore this email."
        )
        msg.attach(MIMEText(plain_text, "plain"))
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as server:
            server.ehlo()
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_USER, email, msg.as_string())

        logger.info(f"[2FA] OTP email sent successfully to {email}")

    except Exception as exc:
        logger.warning(f"[2FA] SMTP send failed ({exc}). Printing code to console.")
        print(f"\n==================================================")
        print(f"[2FA EMAIL FALLBACK — SMTP ERROR]")
        print(f"TO      : {email}")
        print(f"OTP CODE: {code}")
        print(f"ERROR   : {exc}")
        print(f"==================================================\n")


class AuthService:
    # In-memory OTP storage for Two-Factor Email Authentication
    _otp_cache: dict[str, dict] = {}

    @classmethod
    def generate_email_otp(cls, email: str, user_id: int | None = None) -> str:
        """
        Generates a secure 6-digit OTP for Two-Step Email Authentication.
        Valid for 10 minutes. Dispatches real SMTP email in a background thread.
        """
        code = f"{random.randint(100000, 999999)}"
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
        cls._otp_cache[email.lower().strip()] = {
            "code": code,
            "expires_at": expires_at,
            "user_id": user_id
        }
        logger.info(f"[2FA] Generated OTP for {email}")

        # Send email in a background thread — non-blocking
        thread = threading.Thread(
            target=_send_otp_email_smtp,
            args=(email, code),
            daemon=True
        )
        thread.start()

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
