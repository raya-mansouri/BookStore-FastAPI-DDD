from datetime import datetime, timedelta
from fastapi import HTTPException
import pytz
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import func
from app.adapters.repositories.abstract_repo import AbstractRepository
from app.book.domain.entities import Book
from app.reservation.domain.entities import Reservation

iran_timezone = pytz.timezone("Asia/Tehran")
now = datetime.now(iran_timezone)


class ReservationRepository(AbstractRepository[Reservation]):
    def __init__(self, session: AsyncSession):
        """
        Repository for handling reservation-related database operations.

        :param session: The asynchronous SQLAlchemy session.
        """
        super().__init__(session, Reservation)

    async def add(self, reservation: Reservation):
        """
        Adds a reservation to the database, after checking if the book is available.

        :param reservation: The Reservation entity to be added.
        :raises HTTPException: If the book is not found or is fully reserved.
        :raises IntegrityError: If there is a pessimistic lock error.
        """
        query = await self.session.execute(
            select(Book).where(Book.id == reservation.book_id).with_for_update()
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
            raise HTTPException(
                status_code=409, detail="Pessimistic Lock Error. Please try again."
            )

    async def has_read_more_than_3_books(self, customer_id: int) -> bool:
        """
        Checks if a customer has read more than 3 books in the past 30 days.

        :param customer_id: The customer ID to check.
        :return: True if the customer has read more than 3 books, False otherwise.
        """
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
        """
        Checks if a customer has paid more than 300,000 in the past 60 days.

        :param customer_id: The customer ID to check.
        :return: True if the customer has paid more than 300,000, False otherwise.
        """
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
        """
        Counts the number of active reservations for a customer.

        :param customer_id: The customer ID to check.
        :return: The number of active reservations.
        """
        stmt = select(Reservation).where(
            Reservation.customer_id == customer_id, Reservation.status == "active"
        )
        result = await self.session.execute(stmt)
        return len(result.scalars().all())

    async def get_reservation_by_id_and_customer(
        self, reservation_id: int, customer_id: int
    ) -> Reservation | None:
        """
        Retrieves a reservation by its ID and associated customer ID.

        :param reservation_id: The ID of the reservation to retrieve.
        :param customer_id: The customer ID associated with the reservation.
        :return: The found Reservation entity or None if not found.
        """
        stmt = select(Reservation).where(
            Reservation.id == reservation_id, Reservation.customer_id == customer_id
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_all_active_reservations(self) -> list[Reservation] | None:
        """
        Retrieves all active reservations.

        :return: A list of active Reservation entities or None if none are found.
        :raises HTTPException: If no active reservations are found.
        """
        stmt = select(Reservation).where(Reservation.status == "active")
        result = await self.session.execute(stmt)
        if not result:
            raise HTTPException(status_code=404, detail="No reservation found.")
        return result.scalars().all()
