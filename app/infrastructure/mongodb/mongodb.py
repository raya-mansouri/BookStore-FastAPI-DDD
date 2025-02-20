from motor.motor_asyncio import AsyncIOMotorClient
from app.settings import settings

COLLECTION_NAME = "books"

# Create an asynchronous MongoDB client using the credentials from settings
mongo_client = AsyncIOMotorClient(
    f"mongodb://{settings.MONGO_USER}:{settings.MONGO_PASSWORD}@localhost:27017/?authSource=admin"
)

# Access the 'bookstore' database
mongo_db = mongo_client["bookstore"]

# Access the 'books' collection within the 'bookstore' database
books_collection = mongo_db[COLLECTION_NAME]


async def init_mongo():
    collections = await mongo_db.list_collection_names()
    if COLLECTION_NAME not in collections:
        await mongo_db.create_collection(COLLECTION_NAME)
        await mongo_db[COLLECTION_NAME].insert_one({"message": "Hello, MongoDB!"})
        print("MongoDB initialized: Database and collection created.")
