from datetime import datetime, timedelta
from app.adapters.repositories.reservation_repo import ReservationRepository
from app.db.unit_of_work import UnitOfWork
from app.infrastructure.rabbitmq.publish_rabbitmq import publish_event


async def check_reservations_ending_soon():

    async with UnitOfWork() as uow:
        repo = uow.get_repository(ReservationRepository)
        reservations = await repo.get_all_active_reservations()
        for reservation in reservations:
            end_of_reservation = reservation.end_of_reservation
            if end_of_reservation - timedelta(days=1) <= datetime.now():
                # Publish an event to remind the customer one day before the reservation ends
                event = {
                    "event_type": "reservation_ending_soon",
                    "reservation": {
                        "customer_id": reservation.customer_id,
                        "book_id": reservation.book_id,
                        "end_of_reservation": end_of_reservation.isoformat(),
                    }
                }
                publish_event(event)