from typing import TypeVar, Generic, Type, Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import Executable
from sqlalchemy.engine import Result

T = TypeVar("T")


class AbstractRepository(Generic[T]):
    def __init__(self, session: AsyncSession, model: Type[T]):
        self.session = session
        self.model = model

    async def add(self, entity: T) -> None:
        self.session.add(entity)
        await self.session.flush()

    async def remove(self, entity: T) -> None:
        await self.session.delete(entity)
        await self.session.flush()

    async def get(
        self, entity_id: int, with_relations: Optional[list] = None
    ) -> Optional[T]:
        stmt = select(self.model).where(self.model.id == entity_id)
        if with_relations:
            for relation in with_relations:
                stmt = stmt.options(selectinload(relation))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list(self, limit: int = 100, offset: int = 0) -> Sequence[T]:
        stmt = select(self.model).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def update(self, entity_id: int, **kwargs) -> Optional[T]:
        stmt = select(self.model).where(self.model.id == entity_id).with_for_update()
        result = await self.session.execute(stmt)
        entity = result.scalar_one_or_none()
        if entity:
            for key, value in kwargs.items():
                setattr(entity, key, value)
            await self.session.flush()
        return entity

    async def execute(self, stmt: Executable) -> Result:
        return await self.session.execute(stmt)
