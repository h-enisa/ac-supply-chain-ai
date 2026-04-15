from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    APP_NAME: str = "American Computers Supply Chain API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/ac_logistics_db"

    SECRET_KEY: str = "change-this-in-production"

    MODEL_DIR: str = "app/ml/trained_models"

    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:5500",
    ]

    RESEND_API_KEY:    str = ""
    RESEND_FROM_EMAIL: str = "onboarding@resend.dev"
    FRONTEND_URL:      str = "http://localhost:3000"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()