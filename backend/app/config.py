"""
Configuration module for the Multi-Agent Customer Chat system.
Handles environment variables and application settings.
"""

from pydantic import Field
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Database configuration
    database_url: str = Field(..., env="DATABASE_URL")
    
    # Redis configuration
    redis_url: str = Field(..., env="REDIS_URL")
    
    # AI configuration
    google_api_key: Optional[str] = Field(None, env="GOOGLE_API_KEY")
    
    # Application configuration
    environment: str = Field("development", env="ENVIRONMENT")
    debug: bool = Field(False, env="DEBUG")
    
    # Server configuration
    host: str = Field("0.0.0.0", env="HOST")
    port: int = Field(8000, env="PORT")
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings() 