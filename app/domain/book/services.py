from typing import List, Optional
from fastapi import HTTPException
from app.db.unit_of_work import UnitOfWork
from app.domain.book.entities import Book, BookCreate, BookUpdate
from app.repositories.author_repo import AuthorRepository
from app.repositories.book_repo import BookRepository


class BookService:
    async def create_item(self, book_data: BookCreate, uow: UnitOfWork) -> Optional[Book]:
        repo = uow.get_repository(BookRepository)
        
        for key, value in book_data.model_dump(exclude_none=True).items():
            setattr(book_data, key, value)
        
        if book_data.author_ids:
            authors = await self.get_authors_by_ids(uow, book_data.author_ids)
        
        book_data = Book(
            title=book_data.title,
            isbn=book_data.isbn,
            price=book_data.price,
            genre_id=book_data.genre_id,
            description=book_data.description,
            units=book_data.units,
            authors=authors
        )
        await repo.add(book_data)

    async def get_authors_by_ids(self, uow: UnitOfWork, author_ids: List[int]):
        repo = uow.get_repository(AuthorRepository)
        authors = await repo.get_by_ids(author_ids)
        return authors

    async def get_item(self, id: int, uow: UnitOfWork) -> Book:
        repo = uow.get_repository(BookRepository)
        result = await repo.get(id) 
        if not result:
            raise HTTPException(status_code=404, detail="Book not found")
        author_ids = await repo.get_author_ids_from_books(id)
        result.author_ids = author_ids
        return result
    
    async def get_items(self, uow: UnitOfWork, skip: int, limit: int) -> List[Book]:
        repo = uow.get_repository(BookRepository)
        result = await repo.get_book_list(skip, limit)
        if not result:
            raise HTTPException(status_code=404, detail="No books found")
        for book in result:
            author_ids = await repo.get_author_ids_from_books(book.id)
            book.author_ids = author_ids
        return result

    async def update_item(self, id: int, book_data: BookUpdate, uow: UnitOfWork):
        repo = uow.get_repository(BookRepository)
        old_book = await repo.get(id)
        if not old_book:
            raise HTTPException(status_code=404, detail="Book not found")
        
        result = await repo.update(book_data)

        if not result:
            raise HTTPException(status_code=404, detail="Book update failed")
        author_ids = await repo.get_author_ids_from_books(id)
        result.author_ids = author_ids
        return result

    async def delete_item(self, id: int, uow: UnitOfWork):
        repo = uow.get_repository(BookRepository)
        return repo.delete_book_by_id(id)
