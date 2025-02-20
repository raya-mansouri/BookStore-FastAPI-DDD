from typing import List
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

# Setting up Redis client to manage OTP rate limiting
redis_client = Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB0,
    decode_responses=True,
)

rate_limiter = RateLimiter(
    redis_client, "otp_requests"
)  # Rate limiter instance to control OTP request rate

# SMS service setup with multiple providers for sending messages
sms_service = SmsService([SmsIR(), KaveNegar(), Signal()])


class CustomerService:
    # Method to create a new customer
    async def create_item(self, customer_data: CustomerCreate, uow: UnitOfWork):
        async with uow:
            repo = uow.get_repository(
                CustomerRepository
            )  # Getting repository for customer
            new_customer = await repo.create_item(
                customer_data
            )  # Creating new customer
            await uow.commit()  # Committing changes
            await uow.refresh(
                new_customer
            )  # Refreshing the customer data to get the latest state
            return new_customer

    # Method to retrieve a single customer by ID
    async def get_item(self, id: int, uow: UnitOfWork) -> Customer:
        async with uow:
            repo = uow.get_repository(
                CustomerRepository
            )  # Getting repository for customer
            result = await repo.get(id)  # Fetching the customer by ID
            if not result:
                raise HTTPException(
                    status_code=404, detail="Customer not found"
                )  # If customer not found, raise error
            return result

    # Method to get a list of all customers
    async def get_items(self, uow: UnitOfWork) -> List[Customer]:
        async with uow:
            repo = uow.get_repository(
                CustomerRepository
            )  # Getting repository for customer
            return await repo.list()  # Fetching all customers

    # Method to update customer details
    async def update_item(
        self, id: int, customer_data: CustomerUpdate, uow: UnitOfWork
    ):
        async with uow:
            repo = uow.get_repository(
                CustomerRepository
            )  # Getting repository for customer
            updated_customer = await repo.update_item(
                id, customer_data
            )  # Updating customer data
            await uow.commit()  # Committing the changes
            await uow.refresh(updated_customer)  # Refreshing the updated customer data
            return updated_customer

    # Method to delete a customer
    async def delete_item(self, id: int, uow: UnitOfWork):
        async with uow:
            repo = uow.get_repository(
                CustomerRepository
            )  # Getting repository for customer
            deleted_customer = await repo.delete_item(id)  # Deleting the customer
            await uow.commit()  # Committing the changes
            return deleted_customer

    # Method to charge the wallet of a customer
    async def charge_wallet(
        self, user_id: int, amount: int, uow: UnitOfWork
    ) -> Customer:
        async with uow:
            repo = uow.get_repository(
                CustomerRepository
            )  # Getting repository for customer
            customer = await repo.get_by_user_id(
                user_id
            )  # Fetching customer by user ID
            if not customer:
                raise HTTPException(
                    status_code=404, detail="Customer not found"
                )  # If customer not found, raise error
            customer.charge_wallet(amount)  # Charging the customer's wallet
            await uow.commit()  # Committing the changes
            return customer

    # Method to upgrade the subscription model of a customer
    async def upgrade_subscription(
        self, user_id: int, subscription_model: str, uow: UnitOfWork
    ) -> Customer:
        async with uow:
            try:
                repo = uow.get_repository(
                    CustomerRepository
                )  # Getting repository for customer
                customer = await repo.get_by_user_id(
                    user_id
                )  # Fetching customer by user ID

                if not customer:
                    raise HTTPException(
                        status_code=404, detail="Customer not found"
                    )  # If customer not found, raise error

                customer.upgrade_subscription(
                    subscription_model
                )  # Upgrading the subscription model
                await uow.commit()  # Committing the changes
                return customer
            except (
                ValueError
            ) as e:  # If there is a ValueError (e.g., invalid subscription model), raise error
                raise HTTPException(status_code=400, detail=str(e))
