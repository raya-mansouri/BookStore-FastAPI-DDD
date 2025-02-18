from typing import Optional, List
from sqlalchemy import and_, select, update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm.exc import StaleDataError
from sqlalchemy.ext.asyncio import AsyncSession
from app.book.domain.entities import Book
from app.exceptions import NotFoundException
from app.adapters.repositories.abstract_repo import AbstractRepository


class BookRepository(AbstractRepository[Book]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Book)

    async def get_book_list(self, skip: int, limit: int) -> List[Book]:
        return await super().list(limit, skip)

    async def add_book(self, book: Book) -> None:
        await super().add(book)

    async def update_book(self, book_id: int, book_data: dict) -> Optional[Book]:
        existing_book = await self.get_book_by_id(book_id)

        if not existing_book:
            raise NoResultFound("Book not found.")

        stmt = update(Book).where(Book.id == book_id).values(**book_data)
        await self.execute(stmt)

        return await self.get_book_by_id(book_id)

    async def get_book_by_id(
        self, book_id: int, with_relations: Optional[List[str]] = None
    ) -> Optional[Book]:
        return await super().get(book_id, with_relations)

    async def delete_book_by_id(self, book_id: int) -> bool:
        book = await self.get_book_by_id(book_id)
        if not book:
            return {"message": "Book not found."}
        await super().remove(book)
        return {"message": "Book deleted successfully."}

    # async def reserve_book(self, book_id: int, reservation_id: int):
    #     book = await self.get_book_by_id(book_id)
    #     if not book:
    #         raise NoResultFound("Book not found.")

    #     book.set_to_reserved(reservation_id)
    #     stmt = (
    #         update(Book)
    #         .where(Book.id == book_id)
    #         .values()
    #     )

    #     result = await self.execute(stmt)

    #     return await self.get_book_by_id(book_id)

    async def get_author_ids_from_books(self, book_id: int) -> List[int]:
        stmt = select(Book.authors).where(Book.id == book_id)
        result = await self.session.execute(stmt)
        author_ids = result.scalars().all()

        if not author_ids:
            raise NotFoundException("No authors found for the provided book IDs.")

        return author_ids
