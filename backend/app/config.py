"""App settings, read from backend/.env (or real environment variables)."""

from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/.env — found the same way no matter which folder you start the server from.
ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")

    # Every value has a default, so the app still starts (in mock mode) without a .env file.
    LLM_PROVIDER: Literal["mock", "openai", "anthropic"] = "mock"

    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"

    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-opus-5-5"

    JWT_SECRET: str = "change-me"
    DATABASE_URL: str = "sqlite:///./chatbot.db"
    FRONTEND_ORIGIN: str = "http://localhost:3000"
    SYSTEM_PROMPT: str = "You are a helpful assistant."


# Import this one object everywhere: `from app.config import settings`
settings = Settings()
