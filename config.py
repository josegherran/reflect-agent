from pydantic import BaseSettings, Field
from typing import Optional

class Settings(BaseSettings):
    app_env: str = Field("development", env="APP_ENV")
    debug: bool = Field(True, env="DEBUG")
    database_url: str = Field(..., env="DATABASE_URL")
    secret_key: str = Field(..., env="SECRET_KEY")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
