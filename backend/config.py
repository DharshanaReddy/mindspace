from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Groq (free — get key at console.groq.com)
    groq_api_key: str
    groq_model: str = "llama-3.1-70b-versatile"

    # OpenAI (optional)
    openai_api_key: str = ""

    # LangSmith
    langchain_tracing_v2: bool = True
    langchain_api_key: str = ""
    langchain_project: str = "mindspace"
    langchain_endpoint: str = "https://api.smith.langchain.com"

    # Database
    database_url: str = "sqlite+aiosqlite:///./mindspace.db"

    # Auth
    jwt_secret: str = "change-this-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_hours: int = 24

    # App
    app_env: str = "development"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()
