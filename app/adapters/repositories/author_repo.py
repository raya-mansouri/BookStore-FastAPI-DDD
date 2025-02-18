from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.user.entities import Author
from app.adapters.repositories.abstract_repo import AbstractRepository
from app.exceptions import NotFoundException


class AuthorRepository(AbstractRepository[Author]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Author)

    async def get_by_id(self, author_id: int) -> Author:
        author = await super().get(author_id)
        if author is None:
            raise NotFoundException("Author not found.")
        return author

    async def get_by_ids(self, author_ids: List[int]) -> List[Author]:
        stmt = select(Author).where(Author.id.in_(author_ids))
        result = await self.session.execute(stmt)
        authors = result.scalars().all()

        if not authors:
            raise NotFoundException("One or more authors not found.")

        return authors
