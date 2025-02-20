from motor.motor_asyncio import AsyncIOMotorClient
from app.settings import settings

mongo_client = AsyncIOMotorClient(f"mongodb://{settings.MONGO_USER}:{settings.MONGO_PASSWORD}@localhost:27017/?authSource=admin")
mongo_db = mongo_client["bookstore"]
books_collection = mongo_db["books"]
