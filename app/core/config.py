from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str
    SECRET_KEY: str
    DATABASE_URL: str
    ALGORITHM: str
    CORS_ORIGINS: str

    model_config = ConfigDict(env_file=".env")


settings = Settings()
