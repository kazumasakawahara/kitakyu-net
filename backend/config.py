"""
Configuration management for kitakyu-net application.
"""
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

# Load environment variables
load_dotenv()

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Project settings
    project_name: str = "kitakyu-net"
    project_root: Path = PROJECT_ROOT
    data_root: Path = PROJECT_ROOT / "data"
    log_level: str = "INFO"

    # Neo4j settings
    neo4j_uri: str = Field(default="bolt://localhost:7687", alias="NEO4J_URI")
    neo4j_user: str = Field(default="neo4j", alias="NEO4J_USER")
    neo4j_password: str = Field(default="password", alias="NEO4J_PASSWORD")
    neo4j_database: str = Field(
        default="kitakyu-facilities", alias="NEO4J_DATABASE"
    )

    # Ollama LLM settings
    ollama_base_url: str = Field(
        default="http://localhost:11434", alias="OLLAMA_BASE_URL"
    )
    ollama_model: str = Field(default="gpt-oss:20b", alias="OLLAMA_MODEL")
    ollama_temperature: float = Field(default=0.3, alias="OLLAMA_TEMPERATURE")
    ollama_max_tokens: int = Field(default=512, alias="OLLAMA_MAX_TOKENS")
    ollama_timeout: int = Field(default=30, alias="OLLAMA_TIMEOUT")

    # RAG settings
    rag_max_results: int = 10
    rag_cache_ttl: int = 300  # 5 minutes

    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = True

    # Streamlit settings
    streamlit_port: int = 8501

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        populate_by_name = True
        extra = "ignore"  # Ignore extra fields in .env


# Global settings instance
settings = Settings()
