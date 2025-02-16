from fastapi import HTTPException
from fastapi.responses import RedirectResponse
from datetime import datetime, timedelta
import redis, pytz
from app.settings import settings
from app.db.unit_of_work import UnitOfWork
from app.domain.book.entities import Book
from app.domain.reservation.entities import QueueResponseSchema, Reservation
from app.domain.user.entities import Customer
from app.repositories.book_repo import BookRepository
from app.repositories.customer_repo import CustomerRepository
from app.repositories.reservation_repo import ReservationRepository

redis_client = redis.Redis(
            host=settings.REDIS_HOST, 
            port=settings.REDIS_PORT, 
            db=settings.REDIS_DB1
        )
iran_timezone = pytz.timezone("Asia/Tehran")
now = datetime.now(iran_timezone)

class ReservationService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
        # self.customer = await self._get_customer(user_id)

    async def _get_customer(self, user_id):
        repo = self.uow.get_repository(CustomerRepository)
        customer = await repo.get_by_user_id(user_id) 
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        return customer
    
    async def _get_book(self, book_id):
        repo = self.uow.get_repository(BookRepository)
        book = await repo.get(book_id)
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        return book

    async def has_read_more_than_3_books(self, customer_id):
        repo = self.uow.get_repository(ReservationRepository)
        result = await repo.has_read_more_than_3_books(customer_id)
        if not result:
            raise HTTPException(status_code=404, detail="No result")
        return result

    async def has_paid_more_than_300k(self, customer_id):
        repo = self.uow.get_repository(ReservationRepository)
        result = await repo.has_paid_more_than_300k(customer_id)
        if not result:
            raise HTTPException(status_code=404, detail="No result")
        return result

    async def check_funds(self, customer, days):
        daily_rate = 1000
        total_cost = days*daily_rate
        # Apply 100% discount if >300,000 Toman spent in 60 days
        if await self.has_paid_more_than_300k(customer.id) :
            total_cost = 0
        # Apply 30% discount if >3 books in the last 30 days
        if await self.has_read_more_than_3_books(customer.id):
            total_cost = int(total_cost*0.7)

        if customer.wallet_money_amount < total_cost:
            remaining_amount = total_cost - customer.wallet_money_amount
            charge_wallet_url = f"/charge-wallet?amount={remaining_amount}"
            raise HTTPException(status_code=402, detail=f"Not enough balance. Please recharge. Redirect to: {charge_wallet_url}")
            # return RedirectResponse(url=charge_wallet_url)

    async def has_paid_more_than_300k(self, customer_id):
        repo = self.uow.get_repository(ReservationRepository)
        result = await repo.count_active_reservations(customer_id)
        if not result:
            raise HTTPException(status_code=404, detail="No result")
        return result
    
    async def validate_reservation(self, customer, days):
        print(1)
        if customer.subscription_model == "free":
            print(2)
            raise HTTPException(status_code=403, detail="Free users cannot reserve books")
        
        max_days = 14 if customer.subscription_model == "premium" else 7
        if days > max_days:
            raise HTTPException(status_code=403, detail="Exceeding reservation limit for subscription tier")
        
        max_units = 10 if customer.subscription_model == "premium" else 5
        active_reservations = await self.has_paid_more_than_300k(customer.id)
        if active_reservations >= max_units:
            raise HTTPException(status_code=403, detail="Reservation limit exceeded")
        
        self.check_funds(customer, days)


    async def reserve(self, user_id, reservation_data):
        book_id = reservation_data.book_id
        days = reservation_data.days

        customer = await self._get_customer(user_id)
        book = await self._get_book(book_id)

        if book.units - book.reserved_units > 0:
            await self.uow.flush()
            return await self.instant_reserve(customer, book, days)
        await self.uow.flush()
        return await self.queue_reserve(customer, book)
    
    async def instant_reserve(self, customer, book, days):
        await self.validate_reservation(customer, days)
        
        # Deduct cost from wallet
        daily_rate = 1000
        total_cost = days * daily_rate
        customer.deduct_from_wallet(total_cost)
        
        # Update book reserved units
        book.reserve_book()
        
        # Create reservation
        reservation = Reservation(
            customer_id=customer.id,
            book_id=book.id,
            start_of_reservation=now,
            end_of_reservation=now + timedelta(days),
            price=total_cost,
            status="active"
        )
        repo = self.uow.get_repository(ReservationRepository)
        await repo.add(reservation)

        # return reservation

    async def queue_reserve(self, customer, book):
        # Add to Redis queue
        queue_key = f"reservation_queue:{book.id}"
        priority = 0 if customer.subscription_model == "premium" else (1 if customer.subscription_model == "plus" else 3)
        redis_client.zadd(queue_key, {customer.id: priority})
        # return {"message": "Added to reservation queue"}
        queue_position = redis_client.zrank(queue_key, customer.id)
        return QueueResponseSchema(
        customer_id=customer.id,
        book_id=book.id,
        queue_position=queue_position + 1,
    )
    
    async def process_queue(self, customer, book, days):
        queue_key = f"reservation_queue:{self.book.id}"
        next_customer_id = redis_client.zrange(queue_key, 0, 0, withscores=True)
        if next_customer_id:
            next_customer_id = int(next_customer_id[0][0])
            next_customer = self._get_customer(next_customer_id)
            
            # Check if the customer has sufficient fund
            await self.validate_reservation(customer, days)
            daily_rate = 1000
            total_cost = days * daily_rate
            if next_customer.wallet_money_amount >= total_cost:
                redis_client.zrem(queue_key, next_customer_id)
                return self.instant_reserve()
            else:
                # Remove customer from queue if they don't have enough funds
                redis_client.zrem(queue_key, next_customer_id)
                return self.process_queue(customer, book)
        return {"message": "No customers in the queue"}

    async def get_reservation_by_id_and_customer(self, reservation_id, customer_id, uow):
        repo = uow.get_repository(ReservationRepository)
        result = await repo.get_reservation_by_id_and_customer(reservation_id, customer_id)
        if not result:
            raise HTTPException(status_code=404, detail="No reservation with that id")
        return result

    async def cancel_reservation(self, user_id, reservation_id: int, uow: UnitOfWork):
        customer = await self._get_customer(user_id)
        customer_id = customer.id
        repo = uow.get_repository(ReservationRepository)
        reservation_value = await repo.get(reservation_id) 

        if not reservation_value:
                    raise HTTPException(status_code=404, detail="Reservation not found")

        reservation = await repo.get_reservation_by_id_and_customer(reservation_id, customer_id)
        if not reservation:
            raise HTTPException(status_code=404, detail="Reservation not found")
        # Refund wallet (if applicable)
        if reservation.status == "active":
            refund_amount = (reservation.end_of_reservation - reservation.start_of_reservation).days * 1000
            customer.charge_wallet(refund_amount)
        
        # Update book reserved units
        book_id = reservation.book_id
        book = await self._get_book(book_id)
        book.cancel_reservation()

        # Update reservation status
        
        repo = uow.get_repository(ReservationRepository)
        await repo.remove(reservation_value)
        
        await uow.flush()
        await uow.refresh(customer)
        return {"message": "Reservation cancelled successfully"}
