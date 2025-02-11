from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.user.entities import Customer
from app.schemas.customer_schema import CustomerCreate, CustomerUpdate
from app.exceptions import InvalidFieldError, NotFoundException

class CustomerRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_item(self, customer_data: CustomerCreate) -> Optional[Customer]:
        try:
            new_customer = Customer(**customer_data.model_dump()) 
            self.db.add(new_customer)
            await self.db.flush()
            await self.db.refresh(new_customer)
            return new_customer
        except InvalidFieldError as e:
            raise InvalidFieldError(f"Customer creation failed: {e}")

    async def get_item(self, id: int) -> Optional[Customer]:
        result = await self.db.execute(select(Customer).where(Customer.id == id))
        return result.scalar()

    async def get_all(self) -> List[Customer]:
        result = await self.db.execute(select(Customer))
        return result.scalars().all()

    async def update_item(self, id: int, customer_data: CustomerUpdate) -> Optional[Customer]:
        try:
            current_customer = await self.get_item(id)
            if not current_customer:
                raise NotFoundException("Customer not found")
            for key, value in customer_data.model_dump(exclude_none=True).items():
                setattr(current_customer, key, value)
            await self.db.flush()
            await self.db.refresh(current_customer)
            return current_customer
        except InvalidFieldError as e:
            raise InvalidFieldError(f"Customer update failed: {e}")

    async def delete_item(self, id: int) -> bool:
        customer = await self.get_item(id)
        if not customer:
            return False
        await self.db.delete(customer)
        return True