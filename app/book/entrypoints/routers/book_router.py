from fastapi.security import OAuth2PasswordBearer
from fastapi import APIRouter, Depends, status
from app.book.domain.entities import BookCreate, BookOut, BookUpdate
from app.book.service_layer.service import BookService
from app.db.unit_of_work import UnitOfWork, get_uow
from app.permissions import permission_required


router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


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
