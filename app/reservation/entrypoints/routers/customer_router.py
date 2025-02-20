from typing import List
from fastapi import APIRouter, Depends, status
from starlette.requests import Request
from starlette.status import HTTP_204_NO_CONTENT
from app.db.unit_of_work import UnitOfWork, get_uow
from app.permissions import permission_required
from app.reservation.domain.entities import CustomerCreate, CustomerOut, CustomerUpdate
from app.reservation.service_layer.customer_service import CustomerService

router = APIRouter()


# Endpoint to create a new customer
@router.post("/", response_model=CustomerOut)
async def create_customers(
    customer: CustomerCreate,  # Data required to create a new customer
    customer_service: CustomerService = Depends(
        CustomerService
    ),  # Injecting the CustomerService
    uow: UnitOfWork = Depends(
        get_uow
    ),  # Injecting the UnitOfWork for database transaction
):
    return await customer_service.create_item(
        customer, uow
    )  # Calling the service to create the customer


# Endpoint to get customer details by their ID
@router.get("/{id}", response_model=CustomerOut)
async def get_customer(
    id: int,  # Customer ID to fetch details
    customer_service: CustomerService = Depends(
        CustomerService
    ),  # Injecting the CustomerService
    uow: UnitOfWork = Depends(
        get_uow
    ),  # Injecting the UnitOfWork for database transaction
):
    return await customer_service.get_item(
        id, uow
    )  # Calling the service to fetch the customer details


# Endpoint to get all customers
@router.get("/", response_model=List[CustomerOut])
async def get_customers(
    customer_service: CustomerService = Depends(
        CustomerService
    ),  # Injecting the CustomerService
    uow: UnitOfWork = Depends(
        get_uow
    ),  # Injecting the UnitOfWork for database transaction
):
    return await customer_service.get_items(
        uow
    )  # Calling the service to fetch all customers


# Endpoint to charge a customer's wallet by a specified amount
@router.patch("/charge-wallet/{amount}", status_code=status.HTTP_204_NO_CONTENT)
@permission_required(
    allow_current_user=True
)  # Ensuring that the current user has permission to perform the action
async def charge_wallet(
    request: Request,  # Request to access user data
    amount: int,  # Amount to charge the wallet
    customer_service: CustomerService = Depends(
        CustomerService
    ),  # Injecting the CustomerService
    uow: UnitOfWork = Depends(
        get_uow
    ),  # Injecting the UnitOfWork for database transaction
):
    user_id = request.state.user_id  # Getting the current user's ID from the request
    return await customer_service.charge_wallet(
        user_id, amount, uow
    )  # Calling the service to charge the wallet


# Endpoint to upgrade a customer's subscription
@router.patch(
    "/upgrade-subscription/{subscription_model}", status_code=status.HTTP_204_NO_CONTENT
)
@permission_required(
    allow_current_user=True
)  # Ensuring that the current user has permission to perform the action
async def upgrade_subscription(
    request: Request,  # Request to access user data
    subscription_model: str,  # The subscription model to upgrade to (free, plus, premium)
    customer_service: CustomerService = Depends(
        CustomerService
    ),  # Injecting the CustomerService
    uow: UnitOfWork = Depends(
        get_uow
    ),  # Injecting the UnitOfWork for database transaction
):
    user_id = request.state.user_id  # Getting the current user's ID from the request
    return await customer_service.upgrade_subscription(
        user_id, subscription_model, uow
    )  # Calling the service to upgrade subscription


# Endpoint to update an existing customer's details
@router.patch("/{id}", response_model=CustomerOut)
async def update_customer(
    id: int,  # Customer ID to update
    customer: CustomerUpdate,  # Data required to update the customer
    customer_service: CustomerService = Depends(
        CustomerService
    ),  # Injecting the CustomerService
    uow: UnitOfWork = Depends(
        get_uow
    ),  # Injecting the UnitOfWork for database transaction
):
    return await customer_service.update_item(
        id, customer, uow
    )  # Calling the service to update the customer details


# Endpoint to delete a customer by their ID
@router.delete("/{id}")
async def delete_customer(
    id: int,  # Customer ID to delete
    customer_service: CustomerService = Depends(
        CustomerService
    ),  # Injecting the CustomerService
    uow: UnitOfWork = Depends(
        get_uow
    ),  # Injecting the UnitOfWork for database transaction
):
    return await customer_service.delete_item(
        id, uow
    )  # Calling the service to delete the customer
