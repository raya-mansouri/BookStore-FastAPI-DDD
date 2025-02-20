from fastapi import HTTPException
from datetime import datetime, timedelta
import redis, pytz
from app.infrastructure.rabbitmq.publish_rabbitmq import publish_event
from app.reservation.domain.entities import QueueResponseSchema, Reservation
from app.settings import settings
from app.db.unit_of_work import UnitOfWork
from app.adapters.repositories.book_repo import BookRepository
from app.adapters.repositories.customer_repo import CustomerRepository
from app.adapters.repositories.reservation_repo import ReservationRepository

# Setting up Redis client
redis_client = redis.Redis(
    host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB1
)

# Set the timezone to Iran Standard Time
iran_timezone = pytz.timezone("Asia/Tehran")
now = datetime.now(iran_timezone)


# ReservationService class is responsible for handling all the reservation logic
class ReservationService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow  # Unit of Work pattern to manage database transactions

    # Method to get the customer by user ID
    async def _get_customer(self, user_id):
        repo = self.uow.get_repository(CustomerRepository)
        customer = await repo.get_by_user_id(user_id)
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        return customer

    # Method to get the book by book ID
    async def _get_book(self, book_id):
        repo = self.uow.get_repository(BookRepository)
        book = await repo.get(book_id)
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        return book

    # Check if the customer has read more than 3 books in the past 30 days
    async def has_read_more_than_3_books(self, customer_id):
        repo = self.uow.get_repository(ReservationRepository)
        result = await repo.has_read_more_than_3_books(customer_id)
        return result

    # Check if the customer has paid more than 300,000 Toman in the last 60 days
    async def has_paid_more_than_300k(self, customer_id):
        repo = self.uow.get_repository(ReservationRepository)
        result = await repo.has_paid_more_than_300k(customer_id)
        return result

    # Check if the customer has enough funds to reserve the book
    async def check_funds(self, customer, days):
        daily_rate = 1000
        total_cost = days * daily_rate

        # Apply discount if customer spent over 300,000 Toman in the last 60 days
        if await self.has_paid_more_than_300k(customer.id):
            total_cost = 0

        # Apply 30% discount if customer read more than 3 books in the last 30 days
        if await self.has_read_more_than_3_books(customer.id):
            total_cost = int(total_cost * 0.7)

        # Check if the customer has sufficient wallet balance
        if customer.wallet_money_amount < total_cost:
            remaining_amount = total_cost - customer.wallet_money_amount
            charge_wallet_url = f"/charge-wallet?amount={remaining_amount}"
            raise HTTPException(
                status_code=402,
                detail=f"Not enough balance. Please recharge. Redirect to: {charge_wallet_url}",
            )

    # Count active reservations of a customer
    async def count_active_reservations(self, customer_id):
        repo = self.uow.get_repository(ReservationRepository)
        result = await repo.count_active_reservations(customer_id)
        return result

    # Validate reservation based on customer subscription and reservation criteria
    async def validate_reservation(self, customer, days):
        if customer.subscription_model == "free":
            raise HTTPException(
                status_code=403, detail="Free users cannot reserve books"
            )

        max_days = 14 if customer.subscription_model == "premium" else 7
        if days > max_days:
            raise HTTPException(
                status_code=403,
                detail="Exceeding reservation limit for subscription tier",
            )

        max_units = 10 if customer.subscription_model == "premium" else 5
        active_reservations = await self.has_paid_more_than_300k(customer.id)
        if active_reservations >= max_units:
            raise HTTPException(status_code=403, detail="Reservation limit exceeded")

        await self.check_funds(customer, days)

    # Reserve a book for the customer (either instantly or via the queue)
    async def reserve(self, user_id, reservation_data):
        book_id = reservation_data.book_id
        days = reservation_data.days

        customer = await self._get_customer(user_id)
        book = await self._get_book(book_id)

        # If book has available units, reserve it instantly
        if book.units - book.reserved_units > 0:
            await self.uow.flush()
            return await self.instant_reserve(customer, book, days)

        # Otherwise, add the reservation to the queue
        await self.uow.flush()
        return await self.queue_reserve(customer, book, days)

    # Reserve a book instantly by deducting from the customer's wallet and creating the reservation
    async def instant_reserve(self, customer, book, days):
        await self.validate_reservation(customer, days)

        daily_rate = 1000
        total_cost = days * daily_rate
        customer.deduct_from_wallet(total_cost)

        reservation = Reservation(
            customer_id=customer.id,
            book_id=book.id,
            start_of_reservation=now,
            end_of_reservation=now + timedelta(days),
            price=total_cost,
            status="active",
        )
        repo = self.uow.get_repository(ReservationRepository)
        await repo.add(reservation)

    # Add the reservation request to a Redis queue if the book is unavailable
    async def queue_reserve(self, customer, book, days):
        queue_key = f"reservation_queue:{book.id}"
        priority = (
            0
            if customer.subscription_model == "premium"
            else (1 if customer.subscription_model == "plus" else 3)
        )
        redis_client.zadd(queue_key, {customer.id: priority})
        queue_position = redis_client.zrank(queue_key, customer.id)
        return QueueResponseSchema(
            customer_id=customer.id,
            book_id=book.id,
            queue_position=queue_position + 1,
        )

    # Process the reservation queue, checking if the next customer has sufficient funds to reserve the book
    async def process_queue(self, customer, book, days):
        queue_key = f"reservation_queue:{book.id}"
        next_customer_id = redis_client.zrange(queue_key, 0, 0, withscores=True)
        if next_customer_id:
            next_customer_id = int(next_customer_id[0][0])
            next_customer = self._get_customer(next_customer_id)

            # Validate reservation and check if the next customer has sufficient funds
            await self.validate_reservation(customer, days)
            daily_rate = 1000
            total_cost = days * daily_rate
            if next_customer.wallet_money_amount >= total_cost:
                redis_client.zrem(queue_key, next_customer_id)
                return self.instant_reserve(next_customer, book, days)
            else:
                # Remove customer from queue if they don't have enough funds
                redis_client.zrem(queue_key, next_customer_id)
                return self.process_queue(customer, book, days)
        return {"message": "No customers in the queue"}

    # Get reservation by ID and customer ID
    async def get_reservation_by_id_and_customer(
        self, reservation_id, customer_id, uow
    ):
        repo = uow.get_repository(ReservationRepository)
        result = await repo.get_reservation_by_id_and_customer(
            reservation_id, customer_id
        )
        if not result:
            raise HTTPException(
                status_code=404,
                detail="No reservation with that id for get_reservation_by_id_and_customer",
            )
        return result

    # Cancel a reservation and refund if applicable
    async def cancel_reservation(self, user_id, reservation_id: int, uow: UnitOfWork):
        customer = await self._get_customer(user_id)
        customer_id = customer.id
        repo = uow.get_repository(ReservationRepository)
        reservation_value = await repo.get(reservation_id)

        if not reservation_value:
            raise HTTPException(status_code=404, detail="Reservation not found")

        reservation = await repo.get_reservation_by_id_and_customer(
            reservation_id, customer_id
        )
        if not reservation:
            raise HTTPException(status_code=404, detail="Reservation not found")

        # Refund the wallet if the reservation is active
        if reservation.status == "active":
            refund_amount = (
                reservation.end_of_reservation - reservation.start_of_reservation
            ).days * 1000
            customer.charge_wallet(refund_amount)

        # Cancel the reservation and update book reserved units
        book_id = reservation.book_id
        book = await self._get_book(book_id)
        book.cancel_reservation()

        repo = uow.get_repository(ReservationRepository)
        await repo.remove(reservation_value)

        # Publish an event to RabbitMQ to notify about reservation cancellation
        publish_event(
            {
                "event_type": "reservation_cancelled",
                "book_id": book_id,
                "customer_id": customer_id,
            }
        )

        await uow.flush()
        await uow.refresh(customer)
        return {"message": "Reservation cancelled successfully"}
