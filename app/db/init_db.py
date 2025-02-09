from app.db.base import metadata
from app.db.config import engine
from adapters.mappers import start_mappers

def init_db():
    metadata.create_all(engine)
    start_mappers()

init_db()
