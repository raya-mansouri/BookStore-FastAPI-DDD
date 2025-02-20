class BookRepositoryMongoDB:
    def __init__(self, books_collection: str):
        """
        Repository for handling book-related operations in MongoDB.

        :param books_collection: The MongoDB collection for storing books.
        """
        self.books_collection = books_collection

    async def book_created(self, book_data: dict):
        """
        Inserts a new book record into the MongoDB collection.

        :param book_data: The book data to be inserted.
        """
        await self.books_collection.insert_one(book_data)

    async def book_updated(self, book_data: dict):
        """
        Updates an existing book record in the MongoDB collection.

        :param book_data: The updated book data, including the book ID.
        """
        await self.books_collection.update_one(
            {"_id": book_data["id"]},
            {"$set": book_data},
        )

    async def book_deleted(self, book_id: int):
        """
        Deletes a book record from the MongoDB collection by its ID.

        :param book_id: The ID of the book to be deleted.
        """
        await self.books_collection.delete_one({"_id": book_id})
