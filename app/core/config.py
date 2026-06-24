"""
Configuration management for the application.

Uses environment variables with sensible defaults.
"""

import os
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables.
    """

    # Environment
    APP_ENV: str = os.getenv("APP_ENV", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "sqlite:///./chatbot.db"
    )

    # API Keys
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    # LangGraph
    LANGGRAPH_DEBUG: bool = os.getenv("LANGGRAPH_DEBUG", "false").lower() == "true"

    # Security
    CORS_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:8000",
    ]
    ALLOWED_HOSTS: List[str] = ["*"]

    # Rate limiting (placeholder)
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD_SECONDS: int = 60

    # Gemini API Configuration
    GEMINI_BASE_URL: str = "https://generativelanguage.googleapis.com/v1beta"
    GEMINI_TIMEOUT_SECONDS: int = 30
    GEMINI_MAX_RETRIES: int = 3

    # Generation config defaults
    GEMINI_TEMPERATURE: float = 0.7
    GEMINI_MAX_OUTPUT_TOKENS: int = 2048
    GEMINI_TOP_P: float = 1.0
    GEMINI_TOP_K: int = 64

    # Application config
    SESSION_TIMEOUT_MINUTES: int = 60

    def validate(self) -> None:
        """
        Validate critical configuration.
        """
        if self.APP_ENV not in ["development", "production"]:
            raise ValueError(f"Invalid APP_ENV: {self.APP_ENV}")

        if not self.GEMINI_API_KEY and self.APP_ENV == "production":
            raise ValueError("GEMINI_API_KEY is required in production")

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
settings.validate()
