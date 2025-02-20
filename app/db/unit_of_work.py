from sqlalchemy.ext.asyncio import AsyncSession
from abc import ABC, abstractmethod
from typing import Type

from app.db.database import SessionLocal


# Abstract base class defining the essential methods for UnitOfWork
class AbstractUnitOfWork(ABC):
    @abstractmethod
    def get_repository(self, repo_class):
        # Retrieve a repository instance based on the provided class
        raise NotImplementedError

    @abstractmethod
    async def commit(self):
        # Commit the current session
        raise NotImplementedError

    @abstractmethod
    async def rollback(self):
        # Rollback any changes made during the session in case of failure
        raise NotImplementedError

    @abstractmethod
    async def refresh(self, item):
        # Refresh the state of a given item (object) from the database
        raise NotImplementedError

    @abstractmethod
    async def flush(self):
        # Flush the session to apply the changes to the database
        raise NotImplementedError


# Concrete implementation of the UnitOfWork pattern
class UnitOfWork(AbstractUnitOfWork):
    def __init__(self):
        # Initialize with an asynchronous session from the SessionLocal factory
        self.session: AsyncSession = SessionLocal()
        self.repositories = {}  # Cache of repository instances for reuse

    def get_repository(self, repo_class):
        # Retrieve a repository, creating it if it hasn't been created yet
        if repo_class not in self.repositories:
            self.repositories[repo_class] = repo_class(self.session)
        return self.repositories[repo_class]

    async def commit(self):
        # Commit the session to persist all changes made during the session
        await self.session.commit()

    async def flush(self):
        # Flush the session to apply changes to the database (without committing)
        await self.session.flush()

    async def rollback(self):
        # Rollback the session, undoing all changes made since the last commit
        await self.session.rollback()

    async def refresh(self, item):
        # Refresh the given item from the database, updating its attributes
        await self.session.refresh(item)

    # Asynchronous context management methods
    async def __aenter__(self):
        # Enter the context, returning the current UnitOfWork instance
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Exit the context, performing rollback if an exception was raised
        if exc_type is not None:
            await self.rollback()
        # Close the session after the context ends
        await self.session.close()


# Factory function to create a new UnitOfWork instance
async def get_uow() -> UnitOfWork:
    return UnitOfWork()
