from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.exceptions import ResponseValidationError
from sqlalchemy.orm import Session
from typing import List
from starlette.requests import Request
from app.db.unit_of_work import UnitOfWork, get_uow
from app.permissions import permission_required
from app.domain.reservation.entities import *
from app.domain.reservation.services import ReservationService

router = APIRouter()


@router.post("/reserve", status_code=status.HTTP_201_CREATED)
@permission_required(allow_current_user=True)
async def reserve_book(
    request: Request,
    reservation_data: ReservationCreateSchema,
    uow: UnitOfWork = Depends(get_uow)
    ):
    async with uow:
        reservation_service = ReservationService(uow)
        user_id = request.state.user_id
        result = await reservation_service.reserve(user_id, reservation_data)
        await uow.commit()
        return result

@router.delete("/cancel/{reservation_id}")
@permission_required(allow_current_user=True)
async def cancel_reservation(
    request: Request,
    reservation_id: int, 
    # reservation_service: ReservationService = Depends(ReservationService),
    uow: UnitOfWork = Depends(get_uow)
    ):
    async with uow:
        user_id = request.state.user_id
        reservation_service = ReservationService(uow)
        result =  await reservation_service.cancel_reservation(user_id, reservation_id, uow)
        await uow.commit()
        return result


# @router.get("/queue/{book_id}", response_model=ReservationQueueSchema)
# async def get_reservation_queue_position(book_id: int, user_id: int = Depends(get_current_user)):
#     return ReservationService.get_queue_position(user_id, book_id)