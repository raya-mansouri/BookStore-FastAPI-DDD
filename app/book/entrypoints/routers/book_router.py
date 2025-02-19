from fastapi.security import OAuth2PasswordBearer
from fastapi import APIRouter, Depends, status
from pika import BlockingConnection, ConnectionParameters
from redis import Redis
from app.book.domain.entities import BookCreate, BookOut, BookUpdate
from app.book.service_layer.service import BookService
from app.db.unit_of_work import UnitOfWork, get_uow
from app.permissions import permission_required
from app.infrastructure.mongodb.mongodb import books_collection


router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Initialize Redis and RabbitMQ connections
redis = Redis(host="localhost", port=6379, db=0)
mq_connection = BlockingConnection(ConnectionParameters("localhost"))

# Dependency to inject BookService
def get_book_service():
    return BookService(cache=redis, mq_connection=mq_connection)

@router.post("/", status_code=status.HTTP_201_CREATED)
# @permission_required(allowed_roles=["admin"])
async def create_book(
    book_data: BookCreate,
    # token: str = Depends(oauth2_scheme),
    book_service: BookService = Depends(BookService),
    uow: UnitOfWork = Depends(get_uow),
):
    async with uow:
        book = await book_service.create_item(book_data, uow)
        await uow.commit()
        # await uow.refresh(book)
        return {"message": "Book created successfully."}


@router.get("/{book_id}", response_model=BookOut)
async def get_book(
    book_id: int,
    book_service: BookService = Depends(BookService),
    uow: UnitOfWork = Depends(get_uow),
):
    async with uow:
        return await book_service.get_item(book_id, uow)

@router.get("/search", response_model=list[BookOut])
async def search_books(
    query: str,
    skip: int = 0,
    limit: int = 100,
):
    
    # Create a text index on the 'title' and 'description' fields
    books_collection.create_index([("title", "text"), ("description", "text")])
    
    results = books_collection.find(
        {"$text": {"$search": query}},
        {"score": {"$meta": "textScore"}},
    ).sort([("score", {"$meta": "textScore"})]).skip(skip).limit(limit)

    return [BookOut(**book) for book in results]

@router.get("/", response_model=list[BookOut])
async def get_all_books(
    skip: int = 0,
    limit: int = 100,
    # book_service: BookService = Depends(BookService),
    uow: UnitOfWork = Depends(get_uow),
):
    async with uow:
        book_service = BookService()
        return await book_service.get_items(uow, skip, limit)


@router.patch("/{book_id}", response_model=BookOut)
# @permission_required(allowed_roles=["admin", "author"])
async def update_book(
    book_id: int,
    update_data: BookUpdate,
    # token: str = Depends(oauth2_scheme),
    book_service: BookService = Depends(BookService),
    uow: UnitOfWork = Depends(get_uow),
):
    async with uow:
        book = await book_service.update_item(book_id, update_data, uow)
        await uow.commit()
    return book


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
# @permission_required(allowed_roles=["admin", "author"])
async def delete_book(
    book_id: int,
    # token: str = Depends(oauth2_scheme),
    book_service: BookService = Depends(BookService),
    uow: UnitOfWork = Depends(get_uow),
):
    async with uow:
        result = await book_service.delete_item(book_id, uow)
        await uow.commit()
        return result
