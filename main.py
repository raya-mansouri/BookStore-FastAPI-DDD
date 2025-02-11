from fastapi import FastAPI
from app.adapters.mappers import start_mappers
from app.db.base import mapper_registry
from app.routers.user_router import router as user_router
from app.routers.customer_router import router as customer_router

start_mappers(mapper_registry)

app = FastAPI()

app.include_router(user_router, prefix="/users", tags=["Users"])
app.include_router(customer_router, prefix="/customers", tags=["Customers"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
