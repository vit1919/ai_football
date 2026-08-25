from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    jwt_secret_key: SecretStr
    algorithm: str
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    google_api_key: str = ""
    llm_default_model: str = "gemini-3.5-flash-lite"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
