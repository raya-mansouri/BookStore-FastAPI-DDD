from fastapi import FastAPI
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.adapters.mappers import start_mappers
from app.db.base import mapper_registry
from app.infrastructure.rabbitmq.consume_rabbitmq import consume_event
from app.reservation.domain.events import check_reservations_ending_soon
from app.user.entrypoints.routers.user_router import router as user_router
from app.reservation.entrypoints.routers.customer_router import router as customer_router
from app.book.entrypoints.routers.book_router import router as book_router
from app.reservation.entrypoints.routers.reservation_router import router as reservation_router


start_mappers(mapper_registry)

scheduler = AsyncIOScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.add_job(consume_event, 'interval', minutes=1)
    scheduler.add_job(check_reservations_ending_soon, 'cron', hour=9, minute=0)
    scheduler.start()
    yield
    scheduler.shutdown()

app = FastAPI(lifespan=lifespan)

app.include_router(user_router, prefix="/users", tags=["Users"])
app.include_router(customer_router, prefix="/customers", tags=["Customers"])
app.include_router(book_router, prefix="/books", tags=["Books"])
app.include_router(reservation_router, prefix="/reservations", tags=["Reservations"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
