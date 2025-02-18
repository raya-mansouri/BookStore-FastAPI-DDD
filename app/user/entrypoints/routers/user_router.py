from typing import List
from fastapi import APIRouter, Depends, status
from app.db.unit_of_work import UnitOfWork, get_uow
from app.user.domain.entities import (
    LoginStep1Request,
    LoginStep2Request,
    Token,
    UserCreate,
    UserOut,
    UserUpdate,
)
from app.user.service_layer.services import AuthService

router = APIRouter()


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(
    user_data: UserCreate,
    auth_service: AuthService = Depends(AuthService),
    uow: UnitOfWork = Depends(get_uow),
):
    return await auth_service.create_item(user_data, uow)


@router.post("/login/step1")
async def login_step1(
    credentials: LoginStep1Request,
    auth_service: AuthService = Depends(AuthService),
    uow: UnitOfWork = Depends(get_uow),
):
    return await auth_service.login_step1(credentials, uow)


@router.post("/login/step2", response_model=Token)
async def login_step2(
    otp_data: LoginStep2Request,
    auth_service: AuthService = Depends(AuthService),
    uow: UnitOfWork = Depends(get_uow),
):
    return await auth_service.login_step2(otp_data, uow)


@router.get("/{id}", response_model=UserOut)
async def get_customer(
    id: int,
    auth_service: AuthService = Depends(AuthService),
    uow: UnitOfWork = Depends(get_uow),
):
    return await auth_service.get_by_id(id, uow)


@router.get("/", response_model=List[UserOut])
async def get_customers(
    auth_service: AuthService = Depends(AuthService),
    uow: UnitOfWork = Depends(get_uow),
):
    return await auth_service.get_items(uow)


@router.patch("/{id}", response_model=UserOut)
async def update_customer(
    id: int,
    customer: UserUpdate,
    auth_service: AuthService = Depends(AuthService),
    uow: UnitOfWork = Depends(get_uow),
):
    return await auth_service.update_item(id, customer, uow)


@router.delete("/{id}")
async def delete_customer(
    id: int,
    auth_service: AuthService = Depends(AuthService),
    uow: UnitOfWork = Depends(get_uow),
):
    return await auth_service.delete_item(id, uow)
