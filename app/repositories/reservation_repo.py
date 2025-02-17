from datetime import datetime, timedelta
from fastapi import HTTPException
import pytz
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import func
from app.domain.book.entities import Book
from app.domain.reservation.entities import Reservation
from app.repositories.abstract_repo import AbstractRepository

iran_timezone = pytz.timezone("Asia/Tehran")
now = datetime.now(iran_timezone)


class ReservationRepository(AbstractRepository[Reservation]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Reservation)

    async def add(self, reservation: Reservation):
            query = await self.session.execute(
                select(Book)
                .where(Book.id == reservation.book_id)
                .with_for_update()  
            )
            book = query.scalar_one_or_none()
            if not book:
                raise HTTPException(status_code=404, detail="Book not found.")

            if book.units - book.reserved_units <= 0:
                raise HTTPException(status_code=400, detail="Book is fully reserved.")

            # Update book reserved units
            book.reserve_book()

            self.session.add(reservation)
            try:
                await self.session.flush()
            except IntegrityError:
                raise HTTPException(status_code=409, detail="Pessimistic Lock Error. Please try again.")

    async def has_read_more_than_3_books(self, customer_id: int) -> bool:
        thirty_days_ago = now - timedelta(days=30)
        books_read = await self.session.execute(
            select(func.count()).where(
                Reservation.customer_id == customer_id,
                Reservation.end_of_reservation >= thirty_days_ago,
                Reservation.status == "completed",
            )
        )
        return books_read.scalar() > 3

    async def has_paid_more_than_300k(self, customer_id: int) -> bool:
        sixty_days_ago = now - timedelta(days=60)
        total_paid = await self.session.execute(
            select(func.sum(Reservation.price)).where(
                Reservation.customer_id == customer_id,
                Reservation.start_of_reservation >= sixty_days_ago,
                Reservation.status == "completed",
            )
        )
        return (total_paid.scalar() or 0) > 300000

    async def count_active_reservations(self, customer_id: int) -> int:
        stmt = select(Reservation).where(
            Reservation.customer_id == customer_id,
            Reservation.status == "active"
        )
        result = await self.session.execute(stmt)
        return len(result.scalars().all())

    async def get_reservation_by_id_and_customer(self, reservation_id: int, customer_id: int) -> Reservation | None:
        stmt = select(Reservation).where(
            Reservation.id == reservation_id,
            Reservation.customer_id == customer_id
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()
