"""
Configuration management using Pydantic Settings.

Loads configuration from environment variables and .env file.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""
    
    # API Keys
    openai_api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(None, env="ANTHROPIC_API_KEY")
    
    # Database
    database_url: str = Field(
        "sqlite:///./doc_generator.db",
        env="DATABASE_URL"
    )
    
    # Redis
    redis_url: str = Field(
        "redis://localhost:6379/0",
        env="REDIS_URL"
    )
    
    # Server
    api_host: str = Field("0.0.0.0", env="API_HOST")
    api_port: int = Field(8000, env="API_PORT")
    debug: bool = Field(False, env="DEBUG")
    
    # LLM Settings
    default_model: str = Field("gpt-4-turbo-preview", env="DEFAULT_MODEL")
    llm_temperature: float = Field(0.3, env="LLM_TEMPERATURE")
    max_tokens: int = Field(2000, env="MAX_TOKENS")
    
    # Use mock LLM if no API keys provided
    use_mock_llm: bool = Field(False, env="USE_MOCK_LLM")
    
    # Rate Limiting
    rate_limit_requests: int = Field(100, env="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(60, env="RATE_LIMIT_WINDOW")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()


def get_llm_manager():
    """
    Factory function to get appropriate LLM manager.
    
    Returns MockLLMManager if no API keys configured,
    otherwise returns real LLMManager.
    """
    
    # Check if we should use mock
    if settings.use_mock_llm or (
        not settings.openai_api_key and not settings.anthropic_api_key
    ):
        from src.core.mock_llm import MockLLMManager
        return MockLLMManager()
    
    # Use real LLM
    from src.core.llm_manager import LLMManager
    return LLMManager(
        openai_api_key=settings.openai_api_key,
        anthropic_api_key=settings.anthropic_api_key,
        default_model=settings.default_model,
        temperature=settings.llm_temperature,
        max_tokens=settings.max_tokens
    )
