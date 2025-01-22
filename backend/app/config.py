from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    APP_NAME: str = "FinSight AI"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "super-secret-key-finsight-ai-demo-mode-production-ready"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./finsight.db"

    # Cache
    REDIS_URL: str = "redis://localhost:6379/0"

    # AI Provider Settings
    DEFAULT_LLM_PROVIDER: str = "DEMO"
    DEMO_MODE: bool = True

    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    HUGGINGFACE_API_TOKEN: str = ""

    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_BEDROCK_MODEL_ID: str = "anthropic.claude-3-5-sonnet-20241022-v2:0"

    HF_SENTIMENT_MODEL: str = "ProsusAI/finbert"
    HF_EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    HF_DEVICE: str = "cpu"

    UPLOAD_DIR: str = "./data/uploads"
    VECTOR_STORE_DIR: str = "./data/vector_store"
    MAX_UPLOAD_SIZE_BYTES: int = 25 * 1024 * 1024  # 25 MB

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()

# Ensure runtime directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.VECTOR_STORE_DIR, exist_ok=True)
os.makedirs("./data/sample_reports", exist_ok=True)
