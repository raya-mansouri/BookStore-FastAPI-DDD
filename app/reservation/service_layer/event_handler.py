
from datetime import datetime, timedelta

from fastapi import HTTPException

from app.adapters.repositories.book_repo import BookRepository
from app.adapters.repositories.customer_repo import CustomerRepository
from app.db.unit_of_work import UnitOfWork
from app.infrastructure.messaging.sms_provider import send_sms

# Event handler to send a reminder SMS before the reservation ends
async def send_reservation_reminder_handler(event):
    async with UnitOfWork() as uow:
        book_id = event.get("book_id")
        customer_id = event.get("customer_id")
        repo = uow.get_repository(BookRepository)
        book = await repo.get(book_id)
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        customer_repo = uow.get_repository(CustomerRepository)
        customer = await customer_repo.get(customer_id)
        if not customer:
            raise HTTPException(
                status_code=404, detail="Customer not found"
            )
    # Event payload contains the reservation info
    reservation_end_date = datetime.strptime(event.get('end_of_reservation'), "%Y-%m-%dT%H:%M:%S")
    reminder_date = reservation_end_date - timedelta(days=1)

    # If today's date is 1 day before the reservation ends, send the SMS
    if datetime.now() >= reminder_date:
        message = f"Reminder: Your reservation for the book '{book.title}' is ending tomorrow."
        # Send SMS via external service
        send_sms(customer.phone_number, message)
        print(f"Sent reminder SMS to customer {customer_id}")

