from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.adapters.repositories.abstract_repo import AbstractRepository
from app.exceptions import NotFoundException
from app.user.domain.entities import Author


class AuthorRepository(AbstractRepository[Author]):
    def __init__(self, db: AsyncSession):
        """
        Repository for handling database operations related to the Author entity.

        :param db: The asynchronous SQLAlchemy session.
        """
        super().__init__(db, Author)

    async def get_by_id(self, author_id: int) -> Author:
        """
        Retrieves an Author entity by its ID. Raises an exception if not found.

        :param author_id: The ID of the author to retrieve.
        :return: The retrieved Author entity.
        :raises NotFoundException: If the author is not found.
        """
        author = await super().get(author_id)
        if author is None:
            raise NotFoundException("Author not found.")
        return author

    async def get_by_ids(self, author_ids: List[int]) -> List[Author]:
        """
        Retrieves multiple Author entities by their IDs. Raises an exception if none are found.

        :param author_ids: A list of author IDs to retrieve.
        :return: A list of retrieved Author entities.
        :raises NotFoundException: If no authors are found.
        """
        stmt = select(Author).where(Author.id.in_(author_ids))
        result = await self.session.execute(stmt)
        authors = result.scalars().all()

        if not authors:
            raise NotFoundException("One or more authors not found.")

        return authors
