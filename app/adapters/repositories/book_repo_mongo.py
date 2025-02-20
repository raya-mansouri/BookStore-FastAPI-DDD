

class BookRepositoryMongoDB:
    def __init__(self, books_collection: str):
        self.books_collection = books_collection

    async def book_created(self, book_data: dict):
        await self.books_collection.insert_one(book_data)

    async def book_updated(self, book_data: dict):
        await self.books_collection.update_one(
            {'_id': book_data['id']},
            {'$set': book_data},
        )

    async def book_deleted(self, book_id: int):
        await self.books_collection.delete_one({'_id': book_id})