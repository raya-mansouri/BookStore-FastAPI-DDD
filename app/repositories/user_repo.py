from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.domain.user.entities import User

class UserRepository:
    @staticmethod
    async def get_users(db: AsyncSession):
        result = await db.execute(select(User))
        return result.scalars().all()

    @staticmethod
    async def create_user(db: AsyncSession, user_entity: User):
        db.add(user_entity)
        await db.commit()
        await db.refresh(user_entity)
        return user_entity
