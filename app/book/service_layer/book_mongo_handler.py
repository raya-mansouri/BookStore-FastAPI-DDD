

class MongoDBHandler:
    def __init__(self, books_collection: str):
        self.books_collection = books_collection

    def handle_book_created(self, book_data: dict):
        self.books_collection.insert_one(book_data)

    def handle_book_updated(self, book_data: dict):
        self.books_collection.update_one(
            {'_id': book_data['id']},
            {'$set': book_data},
        )

    def handle_book_deleted(self, book_id: int):
        self.books_collection.delete_one(book_id)