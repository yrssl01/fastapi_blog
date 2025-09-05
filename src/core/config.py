import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/test.db"
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
database_url = settings.DATABASE_URL


