"""Configuration management for EduPulse AI FastAPI backend."""

import os
from pathlib import Path
from typing import List

from dotenv import load_dotenv

# Base path of the repository
REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# Load environment variables from backend/.env and project root .env
load_dotenv(REPO_ROOT / "backend" / ".env")
load_dotenv(REPO_ROOT / ".env")


class LlamaSettings:
    """Llama 3.1 LLM provider configuration.

    All settings are loaded from environment variables.
    The API key is NEVER logged, NEVER exposed to frontend,
    and NEVER included in API responses.
    """

    API_KEY: str = os.getenv("LLAMA_API_KEY", "")
    BASE_URL: str = os.getenv("LLAMA_BASE_URL", "https://api.groq.com/openai/v1")
    MODEL: str = os.getenv("LLAMA_MODEL", "llama-3.1-70b-versatile")
    TIMEOUT_SECONDS: float = float(os.getenv("LLAMA_TIMEOUT_SECONDS", "30"))
    TEMPERATURE: float = float(os.getenv("LLAMA_TEMPERATURE", "0"))
    MAX_TOKENS: int = int(os.getenv("LLAMA_MAX_TOKENS", "2048"))

    @property
    def is_configured(self) -> bool:
        """Check if Llama API credentials are present."""
        return bool(self.API_KEY)


class Settings:
    """Application settings and runtime constants."""

    PROJECT_NAME: str = "EduPulse AI — Education Welfare Command Center"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DESCRIPTION: str = (
        "Enterprise decision intelligence API for school retention, welfare efficacy, "
        "and physical infrastructure gap monitoring."
    )

    # DuckDB Path
    DUCKDB_PATH: Path = REPO_ROOT / "data" / "processed" / "edupulse.duckdb"
    PROCESSED_DATA_DIR: Path = REPO_ROOT / "data" / "processed"

    # CORS configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "https://datathon-qaqq.onrender.com",
        "https://datathon-gaqq.onrender.com",
        "https://datathon-ruby.vercel.app",
        "*",
    ]

    # Host & Port
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))

    # Llama 3.1 LLM Configuration
    llama: LlamaSettings = LlamaSettings()


settings = Settings()
