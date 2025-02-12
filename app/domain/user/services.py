from typing import List
from jose import jwt
from fastapi import HTTPException
from app.db.unit_of_work import UnitOfWork
from app.domain.user.entities import Customer
from app.domain.user.utils import create_access_token, get_password_hash, verify_password
from app.repositories.user_repo import AuthRepository
from app.repositories.user_repo_redis import AuthRepositoryRedis
from app.schemas.customer_schema import CustomerCreate, CustomerUpdate
from app.repositories.customer_repo import CustomerRepository
from app.domain.user.entities import UserCreate, LoginStep1Request, LoginStep2Request
from app.settings import settings

SECRET_KEY =  settings.SECRET_KEY
ALGORITHM =  settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

class CustomerService:
    async def create_item(self, customer_data: CustomerCreate, uow: UnitOfWork):
        async with uow:
            repo = uow.get_repository(CustomerRepository)
            new_customer = await repo.create_item(customer_data)
            await uow.commit()
            await uow.refresh(new_customer)
            return new_customer

    async def get_item(self, id: int, uow: UnitOfWork) -> Customer:
        async with uow:
            repo = uow.get_repository(CustomerRepository)
            return await repo.get(id)
    
    async def get_items(self, uow: UnitOfWork) -> List[Customer]:
        async with uow:
            repo = uow.get_repository(CustomerRepository)
            return await repo.list()

    async def update_item(self, id: int, customer_data: CustomerUpdate, uow: UnitOfWork):
        async with uow:
            repo = uow.get_repository(CustomerRepository)
            updated_customer = await repo.update_item(id, customer_data)
            await uow.commit()
            await uow.refresh(updated_customer)
            return updated_customer

    async def delete_item(self, id: int, uow: UnitOfWork):
        async with uow:
            repo = uow.get_repository(CustomerRepository)
            deleted_customer = await repo.delete_item(id)
            await uow.commit()
            return deleted_customer

    async def charge_wallet(self, user_id: int, amount: int, uow: UnitOfWork) -> Customer:
        async with uow:
            repo = uow.get_repository(CustomerRepository)
            customer = await repo.get_by_user_id(user_id) 
            if not customer:
                raise HTTPException(status_code=404, detail="Customer not found")
            customer.charge_wallet(amount)
            await uow.commit()
            return customer

    async def upgrade_subscription(self, user_id: int, subscription_model: str, uow: UnitOfWork) -> Customer:
        async with uow:

            try:
                repo = uow.get_repository(CustomerRepository)
                customer = await repo.get_by_user_id(user_id) 

                if not customer:
                    raise HTTPException(status_code=404, detail="Customer not found")
                
                customer.upgrade_subscription(subscription_model)
                await uow.commit()
                return customer            
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))



class AuthService:
    async def create_item(self, user_data: UserCreate, uow: UnitOfWork):
        async with uow:
            repo = uow.get_repository(AuthRepository)
            existing_user = await repo.get_by_username_or_email(user_data.username, user_data.email)
            if existing_user:
                if existing_user.username == user_data.username:
                    raise HTTPException(status_code=400, detail="Username already registered")
                if existing_user.email == user_data.email:
                    raise HTTPException(status_code=400, detail="Email already registered")
            hashed_password = get_password_hash(user_data.password)
            new_user = await repo.create_item(user_data, hashed_password)
            await uow.commit()
            await uow.refresh(new_user)
            return {"message": "User created successfully"}

    async def authenticate_user(self, username: str, password: str, uow: UnitOfWork):
        async with uow:
            repo = uow.get_repository(AuthRepository)
            user = await repo.get_by_username(username)
            if not user or not verify_password(password, user.password):
                return None
            return user

    async def login_step1(self, credentials: LoginStep1Request, uow: UnitOfWork):
        async with uow:
            user = await self.authenticate_user(credentials.username, credentials.password, uow)
            if not user:
                raise HTTPException(status_code=401, detail="Incorrect username or password")
            otp_repo = AuthRepositoryRedis()
            otp = await otp_repo.generate_otp(user.id)
            return {"message": "OTP sent", "otp": otp}

    async def login_step2(self, otp_data: LoginStep2Request, uow: UnitOfWork):
        async with uow:
            repo = uow.get_repository(AuthRepository)
            otp_repo = AuthRepositoryRedis()
            user_id = await otp_repo.verify_otp(otp_data.otp)
            if not user_id:
                raise HTTPException(status_code=400, detail="Invalid OTP")
            user = await repo.get_by_id(int(user_id))
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            access_token = create_access_token({"id": user.id, "sub": user.username, "role": user.role})
            return {"access_token": access_token, "token_type": "bearer"}

    async def get_current_user(self, token: str, uow: UnitOfWork):
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id = payload.get("id")
        username = payload.get("sub")
        if not id or not username:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
        async with uow:
            repo = uow.get_repository(AuthRepository)
            user = await repo.get_by_id(id)
            if not user:
                raise HTTPException(status_code=401, detail="Could not validate credentials")
            return user

    async def get_by_id(self, id: int, uow: UnitOfWork) -> Customer:
        async with uow:
            repo = uow.get_repository(AuthRepository)
            return await repo.get_by_id(id) 
    
    async def get_items(self, uow: UnitOfWork) -> List[Customer]:
        async with uow:
            repo = uow.get_repository(AuthRepository)
            return await repo.get_all()

    async def update_item(self, id: int, user_data: CustomerUpdate, uow: UnitOfWork):
        async with uow:
            repo = uow.get_repository(AuthRepository)
            updated_user = await repo.update_item(id, user_data)
            await uow.commit()
            await uow.refresh(updated_user)
            return updated_user

    async def delete_item(self, id: int, uow: UnitOfWork):
        async with uow:
            repo = uow.get_repository(AuthRepository)
            deleted_user= await repo.delete_item(id)
            await uow.commit()
            return deleted_user


async def get_customer_service() -> CustomerService:
    return CustomerService()

async def get_auth_service() -> AuthService:
    return AuthService()
