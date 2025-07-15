from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    
    class Config:
        env_file = ".env"  # Optional: Explicitly declare .env location

settings = Settings()  # Single source of truth