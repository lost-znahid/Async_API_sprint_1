from fastapi import FastAPI
from app.api.v1 import films, genres, persons
from services.film import create_index
from elasticsearch.exceptions import ConnectionError as ESConnectionError
import logging
from contextlib import asynccontextmanager

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await create_index()
        logger.info("Index creation checked or completed successfully.")
    except ESConnectionError as e:
        logger.error(f"Elasticsearch connection failed: {e}")
        raise e  # приложение не запустится
    except Exception as e:
        logger.error(f"Unexpected error during index creation: {e}")
        raise e
    yield

app = FastAPI(
    title="Movies API",
    description="API для получения информации о фильмах, жанрах и людях",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(films.router, prefix="/api/v1/films", tags=["Фильмы"])
app.include_router(genres.router, prefix="/api/v1/genres", tags=["Жанры"])
app.include_router(persons.router, prefix="/api/v1/persons", tags=["Персоны"])
