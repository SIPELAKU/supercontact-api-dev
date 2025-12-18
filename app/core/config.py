from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str
    SECRET_KEY: str
    DATABASE_URL: str
    ALGORITHM: str
    CORS_ORIGINS: str
    BREVO_API_KEY: str

    class Config:
        env_file = ".env"


settings = Settings()
