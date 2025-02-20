from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.settings import settings

# Create an asynchronous engine that connects to the database using the URL from settings
engine = create_async_engine(settings.DATABASE_URL, echo=True)

# Create an asynchronous sessionmaker bound to the engine. It does not autocommit or autoflush automatically.
SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Alternative sessionmaker setup (commented out) with expiration control
# SessionLocal = async_sessionmaker(bind=engine, autocommit=False, autoflush=False, expire_on_commit=False)


# Dependency to get an async database session
async def get_db():
    # Creating an asynchronous context for the session.
    # The session will automatically be closed once the context is exited.
    async with SessionLocal() as session:
        yield session  # Yields the session for use in the endpoint
