from datetime import datetime, timedelta
from fastapi import HTTPException
from app.adapters.repositories.book_repo import BookRepository
from app.adapters.repositories.customer_repo import CustomerRepository
from app.db.unit_of_work import UnitOfWork
from app.infrastructure.messaging.sms_provider import send_sms


# Event handler to send a reminder SMS before the reservation ends
async def send_reservation_reminder_handler(event):
    async with UnitOfWork() as uow:
        book_id = event.get("book_id")  # Getting the book ID from the event
        customer_id = event.get("customer_id")  # Getting the customer ID from the event

        # Fetching the book details using the BookRepository
        repo = uow.get_repository(BookRepository)
        book = await repo.get(book_id)
        if not book:
            raise HTTPException(
                status_code=404, detail="Book not found"
            )  # Raise an error if the book doesn't exist

        # Fetching the customer details using the CustomerRepository
        customer_repo = uow.get_repository(CustomerRepository)
        customer = await customer_repo.get(customer_id)
        if not customer:
            raise HTTPException(
                status_code=404, detail="Customer not found"
            )  # Raise an error if the customer doesn't exist

    # Event payload contains the reservation info
    reservation_end_date = datetime.strptime(
        event.get("end_of_reservation"), "%Y-%m-%dT%H:%M:%S"
    )  # Parsing the reservation end date
    reminder_date = reservation_end_date - timedelta(
        days=1
    )  # Calculating the reminder date (1 day before the reservation ends)

    # If today's date is 1 day before the reservation ends, send the SMS
    if datetime.now() >= reminder_date:
        message = f"Reminder: Your reservation for the book '{book.title}' is ending tomorrow."  # SMS message content
        # Send SMS via external service
        send_sms(
            customer.phone_number, message
        )  # Sending the SMS to the customer's phone number
        print(
            f"Sent reminder SMS to customer {customer_id}"
        )  # Log the reminder SMS has been sent
