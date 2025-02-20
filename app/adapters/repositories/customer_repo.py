from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from sqlalchemy import select
from app.adapters.repositories.abstract_repo import AbstractRepository
from app.exceptions import InvalidFieldError, NotFoundException
from app.reservation.domain.entities import Customer, CustomerCreate, CustomerUpdate


class CustomerRepository(AbstractRepository[Customer]):
    def __init__(self, db: AsyncSession):
        """
        Repository for handling customer-related database operations.

        :param db: The asynchronous SQLAlchemy session.
        """
        super().__init__(db, Customer)

    async def create_item(self, customer_data: CustomerCreate) -> Optional[Customer]:
        """
        Creates a new customer and adds it to the database.

        :param customer_data: Data used to create the new customer.
        :return: The created Customer entity.
        :raises InvalidFieldError: If customer data is invalid.
        """
        try:
            new_customer = Customer(**customer_data.model_dump())
            self.session.add(new_customer)
            await self.session.flush()
            await self.session.refresh(new_customer)
            return new_customer
        except InvalidFieldError as e:
            raise InvalidFieldError(f"Customer creation failed: {e}")

    async def update_item(
        self, id: int, customer_data: CustomerUpdate
    ) -> Optional[Customer]:
        """
        Updates an existing customer by its ID with the provided data.

        :param id: The ID of the customer to update.
        :param customer_data: Data to update the customer with.
        :return: The updated Customer entity.
        :raises NotFoundException: If the customer is not found.
        :raises InvalidFieldError: If the update data is invalid.
        """
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
        """
        Deletes a customer by its ID from the database.

        :param id: The ID of the customer to delete.
        :return: True if the customer was deleted, False if not found.
        """
        customer = await self.get(id)
        if not customer:
            return False
        await self.session.delete(customer)
        return True

    async def get_by_user_id(self, user_id: int) -> Optional[Customer]:
        """
        Retrieves a customer by the user ID.

        :param user_id: The user ID associated with the customer.
        :return: The found Customer entity or None if not found.
        """
        result = await self.session.execute(
            select(Customer).where(Customer.user_id == user_id)
        )
        return result.scalar()
