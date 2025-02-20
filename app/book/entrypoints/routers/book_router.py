from fastapi.security import OAuth2PasswordBearer
from fastapi import APIRouter, Depends, status
from pika import BlockingConnection, ConnectionParameters
from redis import Redis
from app.settings import settings
from app.book.domain.entities import BookCreate, BookOut, BookUpdate
from app.book.service_layer.service import BookService
from app.db.unit_of_work import UnitOfWork, get_uow
from app.permissions import permission_required
from app.infrastructure.mongodb.mongodb import books_collection


router = APIRouter()

# Initialize Redis and RabbitMQ connections
# Redis will be used for caching purposes, RabbitMQ for message queuing
redis = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB2)
mq_connection = BlockingConnection(ConnectionParameters("localhost"))


# Dependency to inject BookService
# This ensures that the service used by the routes has access to Redis and RabbitMQ
def get_book_service():
    return BookService(cache=redis, mq_connection=mq_connection)

# Route to create a new book
@router.post("/", status_code=status.HTTP_201_CREATED)
# @permission_required(allowed_roles=["admin"])
async def create_book(
    book_data: BookCreate,  # Book creation data
    book_service: BookService = Depends(get_book_service),  # Inject BookService
    uow: UnitOfWork = Depends(get_uow),  # Inject Unit of Work for database transactions
):
    async with uow:  # Ensure that the operations are part of a transaction
        # Create the book using the book service
        book = await book_service.create_item(book_data, uow)
        await uow.commit()  # Commit the transaction
        return {"message": "Book created successfully."}


@router.get("/{book_id}", response_model=BookOut)
# Route to get a book by its ID
async def get_book(
    book_id: int,  # The ID of the book
    book_service: BookService = Depends(get_book_service),  # Inject BookService
    uow: UnitOfWork = Depends(get_uow),  # Inject Unit of Work
):
    async with uow:  # Ensure that the operation is part of a transaction
        # Retrieve the book using the book service
        return await book_service.get_item(book_id, uow)


@router.get("/search", response_model=list[BookOut])
# Route to search for books by title or description
async def search_books(
    query: str,  # The search query
    skip: int = 0,  # Pagination: how many records to skip
    limit: int = 100,  # Pagination: how many records to return
):
    # Create a text index on the 'title' and 'description' fields for searching
    books_collection.create_index([("title", "text"), ("description", "text")])

    # Perform the search query using MongoDB's text search functionality
    results = (
        books_collection.find(
            {"$text": {"$search": query}},  # MongoDB text search filter
            {"score": {"$meta": "textScore"}},  # Return the score for relevance
        )
        .sort([("score", {"$meta": "textScore"})])  # Sort results by score (relevance)
        .skip(skip)  # Apply pagination: skip 'skip' records
        .limit(limit)  # Limit the number of results to 'limit'
    )

    # Return the search results as a list of BookOut objects
    return [BookOut(**book) for book in results]


@router.get("/", response_model=list[BookOut])
# Route to get all books, with pagination
async def get_all_books(
    skip: int = 0,  # Pagination: how many records to skip
    limit: int = 100,  # Pagination: how many records to return
    uow: UnitOfWork = Depends(get_uow),  # Inject Unit of Work for database transactions
):
    async with uow:  # Ensure that the operation is part of a transaction
        book_service = get_book_service()  # Get the BookService
        return await book_service.get_items(uow, skip, limit)  # Retrieve books with pagination


@router.patch("/{book_id}", response_model=BookOut)
# Route to update an existing book by its ID
# @permission_required(allowed_roles=["admin", "author"])
async def update_book(
    book_id: int,  # The ID of the book to update
    update_data: BookUpdate,  # Data to update the book
    book_service: BookService = Depends(get_book_service),  # Inject BookService
    uow: UnitOfWork = Depends(get_uow),  # Inject Unit of Work for database transactions
):
    async with uow:  # Ensure that the operation is part of a transaction
        # Update the book using the book service
        book = await book_service.update_item(book_id, update_data, uow)
        await uow.commit()  # Commit the transaction
    return book  # Return the updated book


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
# Route to delete a book by its ID
# @permission_required(allowed_roles=["admin", "author"])
async def delete_book(
    book_id: int,  # The ID of the book to delete
    book_service: BookService = Depends(get_book_service),  # Inject BookService
    uow: UnitOfWork = Depends(get_uow),  # Inject Unit of Work for database transactions
):
    async with uow:  # Ensure that the operation is part of a transaction
        # Delete the book using the book service
        result = await book_service.delete_item(book_id, uow)
        await uow.commit()  # Commit the transaction
        return result  # Return the result (should be None since it's a 204 No Content)
