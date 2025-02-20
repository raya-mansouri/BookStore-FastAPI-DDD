from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from app.db.unit_of_work import UnitOfWork, get_uow
from app.permissions import permission_required
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


# Endpoint to sign up a new user
@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(
    user_data: UserCreate,
    auth_service: AuthService = Depends(AuthService),
    uow: UnitOfWork = Depends(get_uow),
):
    return await auth_service.create_item(user_data, uow)


# Endpoint for the first step of login (username and password)
@router.post("/login/step1")
async def login_step1(
    credentials: LoginStep1Request,
    auth_service: AuthService = Depends(AuthService),
    uow: UnitOfWork = Depends(get_uow),
):
    return await auth_service.login_step1(credentials, uow)


# Endpoint for the second step of login (OTP verification)
@router.post("/login/step2", response_model=Token)
async def login_step2(
    otp_data: LoginStep2Request,
    auth_service: AuthService = Depends(AuthService),
    uow: UnitOfWork = Depends(get_uow),
):
    return await auth_service.login_step2(otp_data, uow)


# Endpoint to log out and remove the access token cookie
@router.post("/logout")
@permission_required(allowed_roles=["admin"])
async def logout(response: Response, request: Request):
    if "access_token" not in request.cookies:
        raise HTTPException(status_code=400, detail="No token in cookies")

    response.delete_cookie("access_token")
    return {"message": "Token removed from cookies"}


# Endpoint to get a user by their ID
@router.get("/{id}", response_model=UserOut)
async def get_user(
    id: int,
    auth_service: AuthService = Depends(AuthService),
    uow: UnitOfWork = Depends(get_uow),
):
    return await auth_service.get_by_id(id, uow)


# Endpoint to get a list of all users
@router.get("/", response_model=List[UserOut])
async def get_users(
    auth_service: AuthService = Depends(AuthService),
    uow: UnitOfWork = Depends(get_uow),
):
    return await auth_service.get_items(uow)


# Endpoint to update an existing user by their ID
@router.patch("/{id}", response_model=UserOut)
async def update_user(
    id: int,
    user: UserUpdate,
    auth_service: AuthService = Depends(AuthService),
    uow: UnitOfWork = Depends(get_uow),
):
    return await auth_service.update_item(id, user, uow)


# Endpoint to delete a user by their ID
@router.delete("/{id}")
async def delete_user(
    id: int,
    auth_service: AuthService = Depends(AuthService),
    uow: UnitOfWork = Depends(get_uow),
):
    return await auth_service.delete_item(id, uow)
