from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.settings import settings

engine = create_async_engine(settings.DATABASE_URL, echo=True)

SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)
# SessionLocal = async_sessionmaker(bind=engine, autocommit=False, autoflush=False, expire_on_commit=False)


# Dependency to get the async session
async def get_db():
    async with SessionLocal() as session:
        yield session
