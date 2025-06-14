from fastapi import FastAPI
from app.api.v1 import films, genres, persons

app = FastAPI(
    title="Movies API",
    description="API для получения информации о фильмах, жанрах и людях",
    version="1.0.0"
)

app.include_router(films.router, prefix="/api/v1/films", tags=["Фильмы"])
app.include_router(genres.router, prefix="/api/v1/genres", tags=["Жанры"])
app.include_router(persons.router, prefix="/api/v1/persons", tags=["Персоны"])
