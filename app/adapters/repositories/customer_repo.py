from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.user.entities import Customer
from app.adapters.repositories.abstract_repo import AbstractRepository
from app.domain.user.entities import CustomerCreate, CustomerUpdate
from app.exceptions import InvalidFieldError, NotFoundException

class CustomerRepository(AbstractRepository[Customer]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Customer)

    async def create_item(self, customer_data: CustomerCreate) -> Optional[Customer]:
        try:
            new_customer = Customer(**customer_data.model_dump()) 
            self.session.add(new_customer)
            await self.session.flush()
            await self.session.refresh(new_customer)
            return new_customer
        except InvalidFieldError as e:
            raise InvalidFieldError(f"Customer creation failed: {e}")

    async def update_item(self, id: int, customer_data: CustomerUpdate) -> Optional[Customer]:
        try:
            current_customer = await self.get(id)
            if not current_customer:
                raise NotFoundException("Customer not found")
            for key, value in customer_data.model_dump(exclude_none=True).items():
                setattr(current_customer, key, value)
            await self.session.flush()
            await self.session.refresh(current_customer)
            return current_customer
        except InvalidFieldError as e:
            raise InvalidFieldError(f"Customer update failed: {e}")

    async def delete_item(self, id: int) -> bool:
        customer = await self.get(id)
        if not customer:
            return False
        await self.session.delete(customer)
        return True

    async def get_by_user_id(self, user_id: int) -> Optional[Customer]:
        result = await self.session.execute(select(Customer).where(Customer.user_id == user_id))
        return result.scalar()