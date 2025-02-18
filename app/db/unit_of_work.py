from sqlalchemy.ext.asyncio import AsyncSession
from abc import ABC, abstractmethod
from typing import Type

from app.db.database import SessionLocal


class AbstractUnitOfWork(ABC):
    @abstractmethod
    def get_repository(self, repo_class):
        raise NotImplementedError

    @abstractmethod
    async def commit(self):
        raise NotImplementedError

    @abstractmethod
    async def rollback(self):
        raise NotImplementedError

    @abstractmethod
    async def refresh(self, item):
        raise NotImplementedError

    @abstractmethod
    async def flush(self):
        raise NotImplementedError


class UnitOfWork(AbstractUnitOfWork):
    def __init__(self):
        self.session: AsyncSession = SessionLocal()
        self.repositories = {}

    def get_repository(self, repo_class):
        if repo_class not in self.repositories:
            self.repositories[repo_class] = repo_class(self.session)
        return self.repositories[repo_class]

    async def commit(self):
        await self.session.commit()

    async def flush(self):
        await self.session.flush()

    async def rollback(self):
        await self.session.rollback()

    async def refresh(self, item):
        await self.session.refresh(item)

    # Return the UnitOfWork instance for use in `async with`
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            await self.rollback()  # Rollback on exception
        await self.session.close()  # Close the session


# Factory function to create a UnitOfWork instance
async def get_uow() -> UnitOfWork:
    return UnitOfWork()
