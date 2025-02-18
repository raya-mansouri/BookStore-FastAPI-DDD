from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_
from app.domain.user.entities import UserCreate, User, UserUpdate
from app.exceptions import InvalidFieldError, NotFoundException


class AuthRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_username_or_email(self, username: str, email: str) -> Optional[User]:
        result = await self.db.execute(
            select(User).where(or_(User.username == username, User.email == email))
        )
        return result.scalar()

    async def create_item(self, user_data: UserCreate, hashed_password: str) -> User:
        user_data.password = hashed_password
        new_user = User(**user_data.model_dump()) 
        self.db.add(new_user)
        await self.db.flush()
        await self.db.refresh(new_user)
        return new_user

    async def get_by_username(self, username: str) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalar()

    async def get_by_id(self, user_id: int) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar()

    async def get_all(self) -> List[User]:
        result = await self.db.execute(select(User))
        return result.scalars().all()

    async def update_item(self, id: int, user_data: UserUpdate) -> Optional[User]:
        try:
            current_user = await self.get_by_id(id)
            if not current_user:
                raise NotFoundException("User not found")
            for key, value in user_data.model_dump(exclude_none=True).items():
                setattr(current_user, key, value)
            await self.db.flush()
            await self.db.refresh(current_user)
            return current_user
        except InvalidFieldError as e:
            raise InvalidFieldError(f"User update failed: {e}")

    async def delete_item(self, id: int) -> bool:
        user = await self.get_by_id(id)
        if not user:
            return False
        await self.db.delete(user)
        return True
