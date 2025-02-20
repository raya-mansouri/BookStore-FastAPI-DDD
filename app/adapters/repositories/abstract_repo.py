from typing import TypeVar, Generic, Type, Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import Executable
from sqlalchemy.engine import Result

# Define a generic type variable for the repository
T = TypeVar("T")


class AbstractRepository(Generic[T]):
    def __init__(self, session: AsyncSession, model: Type[T]):
        """
        Abstract repository for handling database operations.

        :param session: SQLAlchemy async session for database interaction.
        :param model: The SQLAlchemy model associated with this repository.
        """
        self.session = session
        self.model = model

    async def add(self, entity: T) -> None:
        """
        Adds a new entity to the database and flushes the session.

        :param entity: The entity to be added.
        """
        self.session.add(entity)
        await self.session.flush()

    async def remove(self, entity: T) -> None:
        """
        Removes an entity from the database and flushes the session.

        :param entity: The entity to be removed.
        """
        await self.session.delete(entity)
        await self.session.flush()

    async def get(
        self, entity_id: int, with_relations: Optional[list] = None
    ) -> Optional[T]:
        """
        Retrieves an entity by its ID, optionally loading related data.

        :param entity_id: The ID of the entity to retrieve.
        :param with_relations: A list of related entities to eagerly load.
        :return: The retrieved entity or None if not found.
        """
        stmt = select(self.model).where(self.model.id == entity_id)
        if with_relations:
            for relation in with_relations:
                stmt = stmt.options(selectinload(relation))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list(self, limit: int = 100, offset: int = 0) -> Sequence[T]:
        """
        Retrieves a list of entities with pagination support.

        :param limit: Maximum number of entities to retrieve.
        :param offset: Number of entities to skip.
        :return: A sequence of retrieved entities.
        """
        stmt = select(self.model).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def update(self, entity_id: int, **kwargs) -> Optional[T]:
        """
        Updates an entity with the provided attributes.

        :param entity_id: The ID of the entity to update.
        :param kwargs: Key-value pairs of attributes to update.
        :return: The updated entity or None if not found.
        """
        stmt = select(self.model).where(self.model.id == entity_id).with_for_update()
        result = await self.session.execute(stmt)
        entity = result.scalar_one_or_none()
        if entity:
            for key, value in kwargs.items():
                setattr(entity, key, value)
            await self.session.flush()
        return entity

    async def execute(self, stmt: Executable) -> Result:
        """
        Executes a raw SQLAlchemy statement.

        :param stmt: The SQL statement to execute.
        :return: The result of the execution.
        """
        return await self.session.execute(stmt)
