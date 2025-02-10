from typing import List
from fastapi import APIRouter, Depends, Response
from starlette.status import HTTP_204_NO_CONTENT

from app.db.unit_of_work import UnitOfWork, get_uow
from app.schemas.customer_schema import CustomerCreate, CustomerUpdate, CustomerOut
from app.domain.user.services import CustomerService


router = APIRouter()

@router.post("/", response_model=CustomerOut)
async def create_customers(
    customer: CustomerCreate, 
    customer_service: CustomerService = Depends(CustomerService),
    uow: UnitOfWork = Depends(get_uow)
    ):
    return await customer_service.create_item(customer, uow)

@router.get("/{id}", response_model=CustomerOut)
async def get_customer(
    id: int,
    customer_service: CustomerService = Depends(CustomerService),
    uow: UnitOfWork = Depends(get_uow),
    ):
    return await customer_service.get_item(id, uow)

@router.get("/", response_model=List[CustomerOut])
async def get_customers(
    customer_service: CustomerService = Depends(CustomerService),
    uow: UnitOfWork = Depends(get_uow),
    ):
    return await customer_service.get_items(uow)

@router.patch("/{id}", response_model=CustomerOut)
async def update_customer(
    id: int, 
    customer: CustomerUpdate, 
    customer_service: CustomerService = Depends(CustomerService),
    uow: UnitOfWork = Depends(get_uow)
    ):
    return await customer_service.update_item(id, customer, uow)

@router.delete("/{id}")
async def delete_customer(
    id: int, 
    customer_service: CustomerService = Depends(CustomerService),
    uow: UnitOfWork = Depends(get_uow)
    ):
    return await customer_service.delete_item(id, uow)
