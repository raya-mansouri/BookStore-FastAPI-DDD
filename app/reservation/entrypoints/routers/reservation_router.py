from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.exceptions import ResponseValidationError
from sqlalchemy.orm import Session
from typing import List
from starlette.requests import Request
from app.db.unit_of_work import UnitOfWork, get_uow
from app.permissions import permission_required
from app.reservation.domain.entities import ReservationCreateSchema
from app.reservation.service_layer.reservation_services import ReservationService

router = APIRouter()


# Endpoint to reserve a book for a user
@router.post("/reserve", status_code=status.HTTP_201_CREATED)
@permission_required(
    allow_current_user=True
)  # Ensure that the current user has permission to reserve
async def reserve_book(
    request: Request,  # Request to access user data
    reservation_data: ReservationCreateSchema,  # Data required to create a reservation
    uow: UnitOfWork = Depends(
        get_uow
    ),  # Injecting the UnitOfWork for transaction management
):
    async with uow:  # Using the UnitOfWork context to manage the transaction
        reservation_service = ReservationService(
            uow
        )  # Creating an instance of ReservationService
        user_id = (
            request.state.user_id
        )  # Getting the current user's ID from the request
        result = await reservation_service.reserve(
            user_id, reservation_data
        )  # Calling the service to reserve the book
        await uow.commit()  # Committing the transaction to save changes
        return result  # Returning the result of the reservation process


# Endpoint to cancel a user's reservation
@router.delete("/cancel/{reservation_id}")
@permission_required(
    allow_current_user=True
)  # Ensure that the current user has permission to cancel
async def cancel_reservation(
    request: Request,  # Request to access user data
    reservation_id: int,  # The ID of the reservation to cancel
    uow: UnitOfWork = Depends(
        get_uow
    ),  # Injecting the UnitOfWork for transaction management
):
    async with uow:  # Using the UnitOfWork context to manage the transaction
        user_id = (
            request.state.user_id
        )  # Getting the current user's ID from the request
        reservation_service = ReservationService(
            uow
        )  # Creating an instance of ReservationService
        result = await reservation_service.cancel_reservation(
            user_id, reservation_id, uow
        )  # Calling the service to cancel the reservation
        await uow.commit()  # Committing the transaction to save changes
        return result  # Returning the result of the cancellation process


# Placeholder for future endpoint to get the reservation queue position for a specific book
# @router.get("/queue/{book_id}", response_model=ReservationQueueSchema)
# async def get_reservation_queue_position(book_id: int, user_id: int = Depends(get_current_user)):
#     return ReservationService.get_queue_position(user_id, book_id)
