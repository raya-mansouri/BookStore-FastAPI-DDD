from typing import List
from app.db.unit_of_work import UnitOfWork
from app.domain.user.entities import Customer
from app.schemas.customer_schema import CustomerCreate, CustomerUpdate
from app.repositories.customer_repo import CustomerRepository


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
            return await repo.get_item(id) 
    
    async def get_items(self, uow: UnitOfWork) -> List[Customer]:
        async with uow:
            repo = uow.get_repository(CustomerRepository)
            return await repo.get_all()

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

async def get_customer_service() -> CustomerService:
    return CustomerService()
