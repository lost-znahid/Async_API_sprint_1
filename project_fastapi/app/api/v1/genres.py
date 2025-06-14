from fastapi import APIRouter, HTTPException
from typing import List
from models.genre import Genre
from utils.elastic import search
from utils.cache import get_cache, set_cache

router = APIRouter()
INDEX_NAME = "genres"

@router.get("/", response_model=List[Genre], summary="Получить список жанров")
async def get_genres(page_number: int = 1, page_size: int = 10, sort: str = "name"):
    cache_key = f"genres:{page_number}:{page_size}:{sort}"
    cached = await get_cache(cache_key)
    if cached:
        return cached

    sort_field = sort.lstrip("-")
    sort_order = "desc" if sort.startswith("-") else "asc"

    body = {
        "sort": [{sort_field: {"order": sort_order}}],
        "from": (page_number - 1) * page_size,
        "size": page_size
    }

    es_response = await search(INDEX_NAME, query={"match_all": {}}, from_=(page_number - 1) * page_size, size=page_size)
    hits = es_response["hits"]["hits"]
    result = [hit["_source"] for hit in hits]

    await set_cache(cache_key, result, expire=120)
    return result

@router.get("/{genre_id}", response_model=Genre, summary="Получить жанр по UUID")
async def get_genre(genre_id: str):
    cache_key = f"genre:{genre_id}"
    cached = await get_cache(cache_key)
    if cached:
        return cached

    body = {
        "query": {"term": {"uuid": genre_id}},
        "size": 1
    }
    es_response = await search(INDEX_NAME, query=body)
    hits = es_response["hits"]["hits"]
    if not hits:
        raise HTTPException(status_code=404, detail="Genre not found")

    result = hits[0]["_source"]
    await set_cache(cache_key, result, expire=300)
    return result
