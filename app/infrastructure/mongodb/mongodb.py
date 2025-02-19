# Initialize MongoDB connection
from pymongo import MongoClient


mongo_client = MongoClient("mongodb://localhost:27017/")
mongo_db = mongo_client["bookstore"]
books_collection = mongo_db["books"]