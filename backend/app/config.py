"""
Configuration module for the Multi-Agent Customer Chat system.
Handles environment variables and application settings.
"""

import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from typing import Optional

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Database configuration
    database_url: Optional[str] = None
    
    # Redis configuration
    redis_url: Optional[str] = None
    
    # AI configuration
    google_api_key: Optional[str] = None
    
    # Application configuration
    environment: Optional[str] = None
    debug: bool = False
    
    # Server configuration
    host: str = "0.0.0.0"
    port: int = 8000
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        case_sensitive = False
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Set database_url from environment variables if not provided
        if not self.database_url:
            postgres_user = os.getenv("POSTGRES_USER")
            postgres_password = os.getenv("POSTGRES_PASSWORD")
            postgres_db = os.getenv("POSTGRES_DB")
            self.database_url = f"postgresql://{postgres_user}:{postgres_password}@localhost:5432/{postgres_db}"
        
        # Set Redis URL from environment variables if not provided
        if not self.redis_url:
            self.redis_url = os.getenv("REDIS_URL")
        
        # Set other environment variables if not provided
        if not self.google_api_key:
            self.google_api_key = os.getenv("GOOGLE_API_KEY")
        
        if not self.environment:
            self.environment = os.getenv("ENVIRONMENT")


# Global settings instance
settings = Settings() 