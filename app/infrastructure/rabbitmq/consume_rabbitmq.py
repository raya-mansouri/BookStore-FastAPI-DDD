import json
import aio_pika
import asyncio
from fastapi import HTTPException
from app.db.unit_of_work import UnitOfWork
from app.adapters.repositories.book_repo import BookRepository
from app.adapters.repositories.customer_repo import CustomerRepository
from app.reservation.service_layer.event_handler import (
    send_reservation_reminder_handler,
)
from app.reservation.service_layer.reservation_services import ReservationService


async def consume_event():
    """
    Consumes events from a RabbitMQ queue and processes them based on the event type.

    This function connects to RabbitMQ, listens for events related to reservations,
    and processes them accordingly. It handles different event types such as
    "reservation_cancelled" and "reservation_ending_soon", executing the respective
    business logic.
    """

    async def callback(message: aio_pika.IncomingMessage):
        """
        Callback function for handling the received event message.

        This function processes the message, extracts the event data,
        and performs the corresponding actions depending on the event type.

        :param message: The incoming message containing the event data.
        """
        async with message.process():
            event_data = json.loads(
                message.body
            )  # Parse the message body to get event data
            event_type = event_data.get("event_type")  # Extract event type

            # Handle the "reservation_cancelled" event
            if event_type == "reservation_cancelled":
                async with UnitOfWork() as uow:
                    book_id = event_data.get("book_id")
                    customer_id = event_data.get("customer_id")

                    # Fetch book from the repository
                    repo = uow.get_repository(BookRepository)
                    book = await repo.get(book_id)

                    if not book:
                        raise HTTPException(status_code=404, detail="Book not found")

                    # Fetch customer from the repository
                    customer_repo = uow.get_repository(CustomerRepository)
                    customer = await customer_repo.get(customer_id)

                    if not customer:
                        raise HTTPException(
                            status_code=404, detail="Customer not found"
                        )

                    # Process the reservation cancellation queue
                    await ReservationService.process_queue(customer, book, days=7)

            # Handle the "reservation_ending_soon" event
            elif event_type == "reservation_ending_soon":
                await send_reservation_reminder_handler(event_data)
            else:
                print(f"Unknown event type: {event_type}")

    # Connect to RabbitMQ server and set up the channel
    connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")
    channel = await connection.channel()  # Create a channel for communication

    # Declare the queue to consume messages from
    queue = await channel.declare_queue("reservation_events", durable=True)

    # Start consuming messages from the queue
    await queue.consume(callback)
    print("Waiting for events. To exit press CTRL+C")

    # Block until the connection is closed or the process is interrupted
    await asyncio.Future()
