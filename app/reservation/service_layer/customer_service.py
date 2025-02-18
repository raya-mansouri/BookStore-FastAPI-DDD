from typing import List
from jose import jwt
from fastapi import HTTPException
from redis import Redis
from app.adapters.repositories.customer_repo import CustomerRepository
from app.db.unit_of_work import UnitOfWork
from app.infrastructure.otp_limiter import RateLimiter
from app.reservation.domain.entities import Customer, CustomerCreate, CustomerUpdate
from app.settings import settings
from app.utils.message_interface.sms_service import KaveNegar, Signal, SmsIR, SmsService

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


redis_client = Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB0,
    decode_responses=True,
)

rate_limiter = RateLimiter(redis_client, "otp_requests")

sms_service = SmsService([SmsIR(), KaveNegar(), Signal()])


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
            result = await repo.get(id)
            if not result:
                raise HTTPException(status_code=404, detail="Customer not found")
            return result

    async def get_items(self, uow: UnitOfWork) -> List[Customer]:
        async with uow:
            repo = uow.get_repository(CustomerRepository)
            return await repo.list()

    async def update_item(
        self, id: int, customer_data: CustomerUpdate, uow: UnitOfWork
    ):
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

    async def charge_wallet(
        self, user_id: int, amount: int, uow: UnitOfWork
    ) -> Customer:
        async with uow:
            repo = uow.get_repository(CustomerRepository)
            customer = await repo.get_by_user_id(user_id)
            if not customer:
                raise HTTPException(status_code=404, detail="Customer not found")
            customer.charge_wallet(amount)
            await uow.commit()
            return customer

    async def upgrade_subscription(
        self, user_id: int, subscription_model: str, uow: UnitOfWork
    ) -> Customer:
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
