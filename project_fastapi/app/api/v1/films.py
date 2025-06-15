from fastapi import APIRouter, HTTPException, Query
from typing import List, Annotated

from models.film import Film
from services.film import get_films_list, get_film_by_id

router = APIRouter()
INDEX_NAME = "films"


@router.get("/", response_model=List[Film], summary="Получить список фильмов")
async def get_films(
    page_number: Annotated[int, Query(ge=1, description="Page number")] = 1,
    page_size: Annotated[int, Query(ge=1, le=100, description="Items per page")] = 10,
    sort: Annotated[str, Query(description="Sort by field (use -field for descending)")] = "title",
):
    return await get_films_list(page_number, page_size, sort)


@router.get("/{film_id}", response_model=Film, summary="Получить фильм по UUID")
async def get_film(film_id: str):
    film = await get_film_by_id(film_id)
    if not film:
        raise HTTPException(status_code=404, detail="Film not found")
    return film
