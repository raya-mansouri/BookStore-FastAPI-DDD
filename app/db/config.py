from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.settings import settings

DATABASE_URL =  settings.DATABASE_URL

engine = create_engine(DATABASE_URL)
# engine = create_engine(DATABASE_URL, pool_size=10, max_overflow=20, pool_timeout=30, pool_recycle=1800)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
