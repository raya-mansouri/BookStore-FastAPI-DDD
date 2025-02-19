import json
import aio_pika
import asyncio
from fastapi import HTTPException
from app.db.unit_of_work import UnitOfWork
from app.adapters.repositories.book_repo import BookRepository
from app.adapters.repositories.customer_repo import CustomerRepository
from app.reservation.service_layer.event_handler import send_reservation_reminder_handler
from app.reservation.service_layer.reservation_services import ReservationService


async def consume_event():
    async def callback(message: aio_pika.IncomingMessage):
        async with message.process():
            event_data = json.loads(message.body)
            event_type = event_data.get("event_type")

            if event_type == "reservation_cancelled":
                async with UnitOfWork() as uow:
                    book_id = event_data.get("book_id")
                    customer_id = event_data.get("customer_id")
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
                    await ReservationService.process_queue(customer, book, days=7)
            elif event_type == "reservation_ending_soon":
                await send_reservation_reminder_handler(event_data)
            else:
                print(f"Unknown event type: {event_type}")

    connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")
    channel = await connection.channel()
    queue = await channel.declare_queue("reservation_events", durable=True)

    await queue.consume(callback)
    print("Waiting for events. To exit press CTRL+C")

    await asyncio.Future()
