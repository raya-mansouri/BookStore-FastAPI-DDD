import json
from typing import List, Optional
from fastapi import HTTPException, Response, status
from pika import BlockingConnection
from redis import Redis
from app.adapters.repositories.author_repo import AuthorRepository
from app.adapters.repositories.book_repo import BookRepository
from app.book.domain.entities import Book, BookCreate, BookUpdate
from app.db.unit_of_work import UnitOfWork


class BookService:
    def __init__(self, cache: Redis, mq_connection: BlockingConnection):
        self.cache = cache
        self.mq_connection = mq_connection
        self.mq_channel = self.mq_connection.channel()
        self.mq_channel.queue_declare(queue="book_updates")

    async def create_item(
        self, book_data: BookCreate, uow: UnitOfWork
    ) -> Optional[Book]:
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
            reserved_units=0,
            authors=authors,
        )
        await repo.add(book_data)
        # Publish an event to the message queue
        self.mq_channel.basic_publish(
            exchange='',
            routing_key='book_updates',
            body=json.dumps({
                'event_type': 'book_created',
                'book_id': book_data.id,
                'book_data': book_data.model_dump(),
            })
        )

    async def get_authors_by_ids(self, uow: UnitOfWork, author_ids: List[int]):
        repo = uow.get_repository(AuthorRepository)
        authors = await repo.get_by_ids(author_ids)
        return authors

    async def get_item(self, id: int, uow: UnitOfWork) -> Book:
        cache_key = f"book:{id}"
        cached_book = self.cache.get(cache_key)
        if cached_book:
            return cached_book
        repo = uow.get_repository(BookRepository)
        result = await repo.get(id)
        if not result:
            raise HTTPException(status_code=404, detail="Book not found")
        author_ids = await repo.get_author_ids_from_books(id)
        result.author_ids = author_ids
        # Cache the result
        self.cache.set(cache_key, result, ex=10080)
        return result

    async def get_items(self, uow: UnitOfWork, skip: int, limit: int) -> List[Book]:
        cache_key = f"books:{skip}:{limit}"
        cached_books = self.cache.get(cache_key)
        if cached_books:
            return cached_books
        
        repo = uow.get_repository(BookRepository)
        result = await repo.get_book_list(skip, limit)
        if not result:
            raise HTTPException(status_code=404, detail="No books found")
        for book in result:
            author_ids = await repo.get_author_ids_from_books(book.id)
            book.author_ids = author_ids
        # Cache the result
        self.cache.set(cache_key, result, ex=10080) 
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
        # Publish an event to the message queue
        self.mq_channel.basic_publish(
            exchange="",
            routing_key="book_updates",
            body=json.dumps(
                {
                    "event_type": "book_updated",
                    "book_id": id,
                    "book_data": result.model_dump(),
                }
            ),
        )
        return result

    async def delete_item(self, id: int, uow: UnitOfWork):
        repo = uow.get_repository(BookRepository)
        book = await repo.get(id)
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        await repo.remove(book)
        # Publish an event to the message queue
        self.mq_channel.basic_publish(
            exchange="",
            routing_key="book_updates",
            body=json.dumps(
                {
                    "event_type": "book_deleted",
                    "book_id": id,
                }
            ),
        )
        return Response(
            "Book deleted successfully",
            status_code=status.HTTP_200_OK,
        )
