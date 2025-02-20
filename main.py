from fastapi import FastAPI
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.adapters.mappers import start_mappers
from app.db.base import mapper_registry
from app.infrastructure.mongodb.consume_mongo import consume_book_updates
from app.infrastructure.rabbitmq.consume_rabbitmq import consume_event
from app.reservation.domain.events import check_reservations_ending_soon
from app.user.entrypoints.routers.user_router import router as user_router
from app.reservation.entrypoints.routers.customer_router import (
    router as customer_router,
)
from app.book.entrypoints.routers.book_router import router as book_router
from app.reservation.entrypoints.routers.reservation_router import (
    router as reservation_router,
)

# Start the mappers for the domain entities
start_mappers(mapper_registry)

# Initialize the scheduler to handle background tasks
scheduler = AsyncIOScheduler()


# Context manager for managing the lifespan of the FastAPI application
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Schedule tasks to run at regular intervals
    scheduler.add_job(
        consume_event, "interval", minutes=1
    )  # Consuming events from RabbitMQ every 1 minute
    scheduler.add_job(
        check_reservations_ending_soon, "cron", hour=9, minute=0
    )  # Check reservations ending at 9:00 AM every day
    scheduler.add_job(
        consume_book_updates, "interval", minutes=1
    )  # Consuming book updates from MongoDB every 1 minute
    scheduler.start()  # Start the scheduler
    yield  # Yield control to the FastAPI app lifecycle
    scheduler.shutdown()  # Shutdown the scheduler when the app stops


# Create the FastAPI app with lifespan context management
app = FastAPI(lifespan=lifespan)

# Include routers for different resources, setting API prefix and tags
app.include_router(user_router, prefix="/users", tags=["Users"])  # User-related routes
app.include_router(
    customer_router, prefix="/customers", tags=["Customers"]
)  # Customer-related routes
app.include_router(book_router, prefix="/books", tags=["Books"])  # Book-related routes
app.include_router(
    reservation_router, prefix="/reservations", tags=["Reservations"]
)  # Reservation-related routes

# If this script is executed directly (rather than being imported), run the FastAPI app with Uvicorn
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
