from pymongo import MongoClient


class MongoDBHandler:
    def __init__(self, mongo_uri: str, db_name: str):
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]
        self.books_collection = self.db['books']

    def handle_book_created(self, book_data: dict):
        self.books_collection.insert_one(book_data)

    def handle_book_updated(self, book_data: dict):
        self.books_collection.update_one(
            {'_id': book_data['id']},
            {'$set': book_data},
        )

    def handle_book_deleted(self, book_id: int):
        self.books_collection.delete_one({'_id': book_id})