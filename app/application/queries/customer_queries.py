from fastapi import HTTPException
from app.repositories.customer_repo import CustomerRepository


async def get_customer(self, user_id):
        repo = self.uow.get_repository(CustomerRepository)
        customer = await repo.get_by_user_id(user_id) 
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        return customer
