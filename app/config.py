import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
# Load .env safely from project root
load_dotenv(dotenv_path=BASE_DIR / ".env", override=True)

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Content Creator Marketplace"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Security
    SECRET_KEY: str = "synapse-hackathon-secret-key-2024-ultra-secure-random-string-abc123!"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # Database
    DATABASE_URL: str = f"sqlite:///{BASE_DIR / 'marketplace.db'}"

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def resolve_database_url(cls, v: str | None) -> str:
        if not v:
            return f"sqlite:///{BASE_DIR / 'marketplace.db'}"
        # Safely convert relative SQLite URL to absolute path
        if v.startswith("sqlite:///."):
            rel = v.replace("sqlite:///.", "").lstrip("/\\")
            return f"sqlite:///{BASE_DIR / rel}"
        return v

    # File Storage
    UPLOAD_DIR: str = str(BASE_DIR / "uploads")
    MAX_UPLOAD_SIZE_MB: int = 50
    ALLOWED_EXTENSIONS: list[str] = [
        "mp4", "webm", "mov", "avi",
        "png", "jpg", "jpeg", "webp", "gif",
        "mp3", "wav", "pdf"
    ]

    # Groq AI Provider (https://console.groq.com)
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    GROQ_FALLBACK_MODELS: list[str] = [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "llama3-70b-8192",
        "mixtral-8x7b-32768"
    ]

    # Currency Settings (Primary: INR, Optional: USD)
    PRIMARY_CURRENCY: str = "INR"
    CURRENCY_SYMBOL_INR: str = "₹"
    CURRENCY_SYMBOL_USD: str = "$"
    USD_TO_INR_EXCHANGE_RATE: float = 85.0

    # SMTP Email Settings (for Two-Step Verification OTP)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "Synapse Marketplace <noreply@synapse.ai>"

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

# Ensure uploads directory exists
Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
