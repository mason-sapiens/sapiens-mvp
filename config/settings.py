"""
Configuration settings for Sapiens MVP.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # API Keys
    openai_api_key: str

    # Application
    environment: str = "development"
    log_level: str = "INFO"

    # LLM Configuration
    default_model: str = "gpt-4o"
    max_tokens: int = 4096
    temperature: float = 0.7

    # Vector Store
    chroma_persist_dir: str = "./data/chroma"
    embedding_model: str = "all-MiniLM-L6-v2"

    # Logging
    log_storage_dir: str = "./data/logs"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: list = ["*"]

    class Config:
        env_file = ".env"
        case_sensitive = False


def get_settings() -> Settings:
    """Get application settings."""

    return Settings()
