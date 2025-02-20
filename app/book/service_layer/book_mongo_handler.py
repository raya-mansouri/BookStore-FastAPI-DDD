from typing import Any


class MongoDBHandler:
    def __init__(self, books_collection: Any):
        # The MongoDB collection instance (mocked using Moto)
        self.books_collection = books_collection

    def handle_book_created(self, book_data: dict):
        # Insert a new book document into the MongoDB collection
        self.books_collection.insert_one(book_data)

    def handle_book_updated(self, book_data: dict):
        book_id = book_data.pop("id", None)
        if book_id:
            # Update the existing book document in the MongoDB collection
            self.books_collection.update_one(
                {"_id": book_id},
                {"$set": book_data},
            )

    def handle_book_deleted(self, book_id: int):
        # Delete a book document from the MongoDB collection
        self.books_collection.delete_one({"_id": book_id})
