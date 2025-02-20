from motor.motor_asyncio import AsyncIOMotorClient
from app.settings import settings

# Create an asynchronous MongoDB client using the credentials from settings
mongo_client = AsyncIOMotorClient(
    f"mongodb://{settings.MONGO_USER}:{settings.MONGO_PASSWORD}@localhost:27017/?authSource=admin"
)

# Access the 'bookstore' database
mongo_db = mongo_client["bookstore"]

# Access the 'books' collection within the 'bookstore' database
books_collection = mongo_db["books"]
