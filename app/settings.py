from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # The database URL for connecting to the database (e.g., PostgreSQL, MongoDB)
    DATABASE_URL: str

    # Secret key used for signing JWT tokens (ensure it's kept safe and not exposed)
    SECRET_KEY: str

    # The algorithm used for JWT encryption/decryption
    ALGORITHM: str

    # The expiration time for the access token in minutes
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # Redis configuration settings
    REDIS_HOST: str = "localhost"  # The Redis server host
    REDIS_PORT: int = 6379  # The port to connect to the Redis server
    REDIS_DB0: int = 0  # Redis database 0 (for storing OTPs or caching)
    REDIS_DB1: int = 1  # Redis database 1 (another database for different use cases)
    REDIS_DB2: int = 2  # Redis database 2 (for different use cases)

    # PostgreSQL database configuration
    POSTGRES_USER: str = "raya"  # Username for PostgreSQL
    POSTGRES_PASSWORD: int = 1234  # Password for PostgreSQL
    POSTGRES_DB: str = "db2"  # Name of the PostgreSQL database

    # MongoDB database configuration
    MONGO_USER: str = "raya"  # Username for MongoDB
    MONGO_PASSWORD: int = 1234  # Password for MongoDB

    # RabbitMQ configuration (used for message queue)
    RABBITMQ_USER: str = "guest"  # RabbitMQ username
    RABBITMQ_PASSWORD: str = "guest"  # RabbitMQ password

    # Debugging mode (usually set to False in production)
    DEBUG: bool = False

    # Load environment variables from the .env file
    class Config:
        env_file = ".env"


# Instantiate the settings class to load configuration values
settings = Settings()
