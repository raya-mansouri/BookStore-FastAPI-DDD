from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://raya:1234@postgres_db:5432/db2"

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    
    REDIS_HOST: str = "redis_db"
    REDIS_PORT: int = 6379
    REDIS_DB0: int = 0
    REDIS_DB1: int = 1

    POSTGRES_USER: str = "raya"
    POSTGRES_PASSWORD: int = 1234
    POSTGRES_DB: str = "db2"

    MONGO_USER: str = "raya"
    MONGO_PASSWORD: int = 1234

    DEBUG: bool = False

    class Config:
        env_file = ".env"

settings = Settings()