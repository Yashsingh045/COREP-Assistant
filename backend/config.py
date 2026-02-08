"""
Configuration module for COREP Assistant.
Uses pydantic-settings to load environment variables.
"""
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # OpenAI Configuration
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", env="OPENAI_MODEL")
    openai_embedding_model: str = Field(
        default="text-embedding-3-small", 
        env="OPENAI_EMBEDDING_MODEL"
    )
    
    # Database Configuration
    database_url: str = Field(..., env="DATABASE_URL")
    
    # Application Settings
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    environment: str = Field(default="development", env="ENVIRONMENT")
    
    # Retrieval Settings
    top_k_paragraphs: int = Field(default=5, env="TOP_K_PARAGRAPHS")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
