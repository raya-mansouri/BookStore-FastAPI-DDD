from datetime import datetime, timedelta
from app.adapters.repositories.reservation_repo import ReservationRepository
from app.db.unit_of_work import UnitOfWork
from app.infrastructure.rabbitmq.publish_rabbitmq import publish_event


# Asynchronous function to check if any active reservation is ending soon
async def check_reservations_ending_soon():

    # Using UnitOfWork to ensure all database operations are executed within a transaction
    async with UnitOfWork() as uow:

        # Getting the ReservationRepository to interact with reservation data
        repo = uow.get_repository(ReservationRepository)

        # Fetching all active reservations from the repository
        reservations = await repo.get_all_active_reservations()

        # Iterating through each reservation
        for reservation in reservations:

            # Extracting the end date of the current reservation
            end_of_reservation = reservation.end_of_reservation

            # Checking if the reservation is ending within the next day
            if end_of_reservation - timedelta(days=1) <= datetime.now():

                # Preparing the event to notify the customer about the reservation ending soon
                event = {
                    "event_type": "reservation_ending_soon",  # Event type
                    "reservation": {
                        "customer_id": reservation.customer_id,  # Customer ID
                        "book_id": reservation.book_id,  # Book ID
                        "end_of_reservation": end_of_reservation.isoformat(),  # End date in ISO format
                    },
                }

                # Publishing the event to RabbitMQ to notify the customer
                publish_event(event)
