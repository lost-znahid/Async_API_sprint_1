from fastapi import APIRouter, HTTPException
from typing import List
from models.film import Film
from utils.elastic import search
from utils.cache import get_cache, set_cache

router = APIRouter()
INDEX_NAME = "films"

@router.get("/", response_model=List[Film], summary="Получить список фильмов")
async def get_films(page_number: int = 1, page_size: int = 10, sort: str = "title"):
    cache_key = f"films:{page_number}:{page_size}:{sort}"
    cached = await get_cache(cache_key)
    if cached:
        return cached

    sort_field = sort.lstrip("-")
    sort_order = "desc" if sort.startswith("-") else "asc"

    es_response = await search(INDEX_NAME, query={"match_all": {}}, from_=(page_number - 1) * page_size, size=page_size)
    hits = es_response["hits"]["hits"]
    result = [hit["_source"] for hit in hits]

    await set_cache(cache_key, result, expire=120)
    return result

@router.get("/{film_id}", response_model=Film, summary="Получить фильм по UUID")
async def get_film(film_id: str):
    cache_key = f"film:{film_id}"
    cached = await get_cache(cache_key)
    if cached:
        return cached

    body = {
        "query": {"term": {"uuid": film_id}},
        "size": 1
    }
    es_response = await search(INDEX_NAME, query=body)
    hits = es_response["hits"]["hits"]
    if not hits:
        raise HTTPException(status_code=404, detail="Film not found")

    result = hits[0]["_source"]
    await set_cache(cache_key, result, expire=300)
    return result
