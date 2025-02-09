from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user_repo import UserRepository
from app.domain.user.entities import User
from app.db.database import get_db

router = APIRouter()

@router.get("/users")
async def get_users(db: AsyncSession = Depends(get_db)):
    return await UserRepository.get_users(db)

@router.post("/users")
async def create_user(name: str, db: AsyncSession = Depends(get_db)):
    user_entity = User(name=name)
    return await UserRepository.create_user(db, user_entity)
