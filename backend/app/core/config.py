from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # AWS Configuration
    AWS_REGION: str = "us-east-1"
    COGNITO_USER_POOL_ID: str
    COGNITO_APP_CLIENT_ID: str
    COGNITO_APP_CLIENT_SECRET: str = None
    
    # Lex Configuration
    LEX_BOT_NAME: str
    LEX_BOT_ALIAS: str
    
    # Comprehend Configuration
    COMPREHEND_LANGUAGE_CODE: str = "en"
    
    # Database Configuration
    DATABASE_URL: str
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]  # Next.js default
    
    class Config:
        env_file = ".env"

settings = Settings()