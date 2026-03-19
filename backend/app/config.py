from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/freightos_db"

    class Config:
        env_file = ".env"


settings = Settings()