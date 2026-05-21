from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_env: str = "development"
    debug: bool = False
    database_url: str | None = None
    secret_key: str | None = None


settings = Settings()
