from fastapi import APIRouter, HTTPException, Query
from typing import List, Annotated
from models.genre import Genre
from utils.elastic import search
from utils.cache import get_cache, set_cache

router = APIRouter()
INDEX_NAME = "genres"
ALLOWED_SORT_FIELDS = {"name", "description", "uuid"}

@router.get("/", response_model=List[Genre], summary="Получить список жанров")
async def get_genres(
    page_number: Annotated[int, Query(ge=1, description="Номер страницы")] = 1,
    page_size: Annotated[int, Query(ge=1, le=100, description="Размер страницы")] = 10,
    sort: Annotated[str, Query(description="Поле сортировки, можно с префиксом '-' для убывания")] = "name",
):
    cache_key = f"genres:{page_number}:{page_size}:{sort}"
    cached = await get_cache(cache_key)
    if cached is not None:
        return cached

    sort_field = sort.lstrip("-")
    if sort_field not in ALLOWED_SORT_FIELDS:
        raise HTTPException(status_code=400, detail="Invalid sort field")

    sort_order = "desc" if sort.startswith("-") else "asc"

    body = {
        "query": {"match_all": {}},
        "sort": [{sort_field: {"order": sort_order}}],
        "from": (page_number - 1) * page_size,
        "size": page_size
    }

    es_response = await search(INDEX_NAME, query=body)
    hits = es_response.get("hits", {}).get("hits", [])
    result = [hit["_source"] for hit in hits]

    await set_cache(cache_key, result, expire=120)
    return result

@router.get("/{genre_id}", response_model=Genre, summary="Получить жанр по UUID")
async def get_genre(genre_id: str):
    cache_key = f"genre:{genre_id}"
    cached = await get_cache(cache_key)
    if cached is not None:
        return cached

    body = {
        "query": {"term": {"uuid": genre_id}},
        "size": 1
    }
    es_response = await search(INDEX_NAME, query=body)
    hits = es_response.get("hits", {}).get("hits", [])
    if not hits:
        raise HTTPException(status_code=404, detail="Genre not found")

    result = hits[0]["_source"]
    await set_cache(cache_key, result, expire=300)
    return result
