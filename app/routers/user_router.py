from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user_repo import UserRepository
from app.domain.user.entities import User
from app.db.database import get_db

router = APIRouter()

@router.get("/users")
async def get_users(db: AsyncSession = Depends(get_db)):
    return await UserRepository.get_users(db)

#for test
from pydantic import BaseModel
class UserSchema(BaseModel):
    username: str
    first_name: str
    last_name: str
    phone: str
    email: str
    role: str
    is_active: bool = True

@router.post("/users")
async def create_user(user_data: UserSchema, db: AsyncSession = Depends(get_db)):
    user_entity = User(**user_data.model_dump(exclude_unset=True))
    return await UserRepository.create_user(db, user_entity)
