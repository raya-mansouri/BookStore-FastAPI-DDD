from typing import Optional, List
from sqlalchemy import and_, select, update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from app.book.domain.entities import Book
from app.exceptions import NotFoundException
from app.adapters.repositories.abstract_repo import AbstractRepository


class BookRepository(AbstractRepository[Book]):
    def __init__(self, session: AsyncSession):
        """
        Repository for handling database operations related to the Book entity.

        :param session: The asynchronous SQLAlchemy session.
        """
        super().__init__(session, Book)

    async def get_book_list(self, skip: int, limit: int) -> List[Book]:
        """
        Retrieves a paginated list of books.

        :param skip: Number of records to skip (offset).
        :param limit: Maximum number of records to retrieve.
        :return: A list of Book entities.
        """
        return await super().list(limit, skip)

    async def add_book(self, book: Book) -> None:
        """
        Adds a new book to the database.

        :param book: The Book entity to be added.
        """
        await super().add(book)

    async def update_book(self, book_id: int, book_data: dict) -> Optional[Book]:
        """
        Updates an existing book's attributes.

        :param book_id: The ID of the book to update.
        :param book_data: A dictionary of fields to update.
        :return: The updated Book entity.
        :raises NoResultFound: If the book does not exist.
        """
        existing_book = await self.get_book_by_id(book_id)
        if not existing_book:
            raise NoResultFound("Book not found.")

        stmt = update(Book).where(Book.id == book_id).values(**book_data)
        await self.execute(stmt)

        return await self.get_book_by_id(book_id)

    async def get_book_by_id(
        self, book_id: int, with_relations: Optional[List[str]] = None
    ) -> Optional[Book]:
        """
        Retrieves a book by its ID, optionally loading related entities.

        :param book_id: The ID of the book to retrieve.
        :param with_relations: A list of related fields to eagerly load.
        :return: The retrieved Book entity or None if not found.
        """
        return await super().get(book_id, with_relations)

    async def delete_book_by_id(self, book_id: int) -> bool:
        """
        Deletes a book by its ID.

        :param book_id: The ID of the book to delete.
        :return: A success message.
        """
        book = await self.get_book_by_id(book_id)
        if not book:
            return {"message": "Book not found."}
        await super().remove(book)
        return {"message": "Book deleted successfully."}

    async def get_author_ids_from_books(self, book_id: int) -> List[int]:
        """
        Retrieves the IDs of authors associated with a book.

        :param book_id: The ID of the book.
        :return: A list of author IDs.
        :raises NotFoundException: If no authors are found for the book.
        """
        stmt = select(Book.authors).where(Book.id == book_id)
        result = await self.session.execute(stmt)
        author_ids = result.scalars().all()

        if not author_ids:
            raise NotFoundException("No authors found for the provided book IDs.")

        return author_ids
