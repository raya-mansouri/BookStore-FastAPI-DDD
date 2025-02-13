from pydantic import BaseModel, Field
from datetime import datetime
from app.domain.reservation.object_values import ReservationStatus


class Reservation:
    id: int
    customer_id: int
    book_id: int
    start_of_reservation: datetime
    end_of_reservation: datetime
    status: ReservationStatus
    price: int

    def __init__(
        self,
        customer_id: int,
        book_id: int,
        start_of_reservation: datetime,
        end_of_reservation: datetime,
        status: ReservationStatus,
        price: int
    ):
        self.customer_id = customer_id
        self.book_id = book_id
        self.start_of_reservation = start_of_reservation
        self.end_of_reservation = end_of_reservation
        self.status = status
        self.price = price


class ReservationCreateSchema(BaseModel):
    book_id: int = Field(..., description="ID of the book to reserve")
    days: int = Field(..., description="Number of days for reservation")


class ReservationResponseSchema(BaseModel):
    id: int
    customer_id: int
    book_id: int
    start_of_reservation: datetime
    end_of_reservation: datetime
    status: str


class QueueResponseSchema(BaseModel):
    customer_id: int
    book_id: int
    queue_position: int
