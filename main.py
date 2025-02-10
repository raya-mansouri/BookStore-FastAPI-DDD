from fastapi import FastAPI
from app.adapters.mappers import start_mappers
from app.db.base import mapper_registry
from app.routers.user_router import router


start_mappers(mapper_registry)

app = FastAPI()
app.include_router(router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
