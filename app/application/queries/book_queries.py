from fastapi import HTTPException
from app.adapters.repositories.book_repo import BookRepository

    
async def get_book(self, book_id):
        repo = self.uow.get_repository(BookRepository)
        book = await repo.get(book_id)
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        return book