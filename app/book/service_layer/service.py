import json
import pickle
from typing import List, Optional
from fastapi import HTTPException, Response, status
from pika import BlockingConnection
from redis import Redis
from app.adapters.repositories.author_repo import AuthorRepository
from app.adapters.repositories.book_repo import BookRepository
from app.book.domain.entities import Book, BookCreate, BookOut, BookUpdate
from app.db.unit_of_work import UnitOfWork


class BookService:
    def __init__(self, cache: Redis, mq_connection: BlockingConnection):
        self.cache = cache
        self.mq_connection = mq_connection
        self.mq_channel = self.mq_connection.channel()
        self.mq_channel.queue_declare(queue="book_updates")

    async def create_item(
        self, new_book: BookCreate, uow: UnitOfWork
    ) -> Optional[Book]:
        repo = uow.get_repository(BookRepository)

        for key, value in new_book.model_dump(exclude_none=True).items():
            setattr(new_book, key, value)

        if new_book.author_ids:
            authors = await self.get_authors_by_ids(uow, new_book.author_ids)

        book_data = Book(
            title=new_book.title,
            isbn=new_book.isbn,
            price=new_book.price,
            genre_id=new_book.genre_id,
            description=new_book.description,
            units=new_book.units,
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
                'book_data': new_book.model_dump(),
            })
        )

    async def get_authors_by_ids(self, uow: UnitOfWork, author_ids: List[int]):
        repo = uow.get_repository(AuthorRepository)
        authors = await repo.get_by_ids(author_ids)
        return authors

    async def get_item(self, id: int, uow: UnitOfWork) -> Book | BookOut:
        cache_key = f"book:{id}"
        cached_book = self.cache.get(cache_key)
        if cached_book:
            return BookOut(**json.loads(cached_book))
        repo = uow.get_repository(BookRepository)
        result = await repo.get(id)
        if not result:
            raise HTTPException(status_code=404, detail="Book not found")
        author_ids = await repo.get_author_ids_from_books(id)
        result.author_ids = author_ids
        # Cache the result
        book_dict = {c.name: getattr(result, c.name) for c in result.__table__.columns}
        book_dict["author_ids"] = author_ids  
        serialized_book = json.dumps(book_dict)
        self.cache.set(cache_key, serialized_book, ex=10080)
        return result

    async def get_items(self, uow: UnitOfWork, skip: int, limit: int) -> List[Book] | list[BookOut]:
        cache_key = f"books:{skip}:{limit}"
        cached_books = self.cache.get(cache_key)
        if cached_books:
            return [BookOut(**book) for book in json.loads(cached_books)]
        
        repo = uow.get_repository(BookRepository)
        result = await repo.get_book_list(skip, limit)
        if not result:
            raise HTTPException(status_code=404, detail="No books found")
        for book in result:
            author_ids = await repo.get_author_ids_from_books(book.id)
            book.author_ids = author_ids
        # Cache the result
        serialized_books = json.dumps([book.to_dict() for book in result])
        self.cache.set(cache_key, serialized_books, ex=10080)
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
