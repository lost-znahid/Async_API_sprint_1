from fastapi import APIRouter, HTTPException
from typing import List
from models.person import Person
from utils.elastic import search
from utils.cache import get_cache, set_cache

router = APIRouter()
INDEX_NAME = "persons"

@router.get("/", response_model=List[Person], summary="Получить список персон")
async def get_persons(page_number: int = 1, page_size: int = 10, sort: str = "full_name"):
    cache_key = f"persons:{page_number}:{page_size}:{sort}"
    cached = await get_cache(cache_key)
    if cached:
        return cached

    sort_field = sort.lstrip("-")
    sort_order = "desc" if sort.startswith("-") else "asc"

    body = {
        "query": {"match_all": {}},
        "sort": [{sort_field: {"order": sort_order}}],
        "from": (page_number - 1) * page_size,
        "size": page_size
    }

    es_response = await search(INDEX_NAME, query=body)
    hits = es_response["hits"]["hits"]
    result = [hit["_source"] for hit in hits]

    await set_cache(cache_key, result, expire=120)
    return result

@router.get("/{person_id}", response_model=Person, summary="Получить персону по UUID")
async def get_person(person_id: str):
    cache_key = f"person:{person_id}"
    cached = await get_cache(cache_key)
    if cached:
        return cached

    body = {
        "query": {"term": {"uuid": person_id}},
        "size": 1
    }
    es_response = await search(INDEX_NAME, query=body)
    hits = es_response["hits"]["hits"]
    if not hits:
        raise HTTPException(status_code=404, detail="Person not found")

    result = hits[0]["_source"]
    await set_cache(cache_key, result, expire=300)
    return result
