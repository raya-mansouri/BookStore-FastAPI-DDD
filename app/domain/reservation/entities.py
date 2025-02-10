from pydantic import BaseModel, Field
from datetime import datetime

class ReservationCreateSchema:
    book_id: int = Field(..., description="ID of the book to reserve")
    days: int = Field(..., description="Number of days for reservation")

class Reservation:
    id: int
    customer_id: int
    book_id: int
    start_of_reservation: datetime
    end_of_reservation: datetime
    status: str

class QueueResponseSchema:
    customer_id: int
    book_id: int
    queue_position: int