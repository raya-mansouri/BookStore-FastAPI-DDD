from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from app.settings import settings  # Adjust according to your project structure

engine = create_async_engine(settings.DATABASE_URL, echo=True)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Dependency to get the async session
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


# Dependency to get the DB session
# async def get_db() -> AsyncSession:
#     async with AsyncSessionLocal() as session:
#         yield session