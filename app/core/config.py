from pydantic_settings import BaseSettings
from typing import Literal
from pydantic import HttpUrl

class Settings(BaseSettings):
    DATABASE_URL: str
    ENV: Literal["local", "prod"] = "prod"  # 기본값 prod
    DISCORD_WEBHOOK_URL: str
    SPRING_SERVER_BASE_URL: HttpUrl
    GOOGLE_APPLICATION_CREDENTIALS: str
    OPENAI_API_KEY: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
