from fastapi import APIRouter, HTTPException, Query
from typing import List, Annotated
from models.person import Person
from utils.elastic import search
from utils.cache import get_cache, set_cache

router = APIRouter()
INDEX_NAME = "persons"
ALLOWED_SORT_FIELDS = {"full_name", "uuid"}

@router.get("/", response_model=List[Person], summary="Получить список персон")
async def get_persons(
    page_number: Annotated[int, Query(ge=1, description="Номер страницы")] = 1,
    page_size: Annotated[int, Query(ge=1, le=100, description="Размер страницы")] = 10,
    sort: Annotated[str, Query(description="Поле сортировки, можно с префиксом '-' для убывания")] = "full_name",
):
    cache_key = f"persons:{page_number}:{page_size}:{sort}"
    cached = await get_cache(cache_key)
    if cached is not None:
        return cached

    sort_field = sort.lstrip("-")
    if sort_field not in ALLOWED_SORT_FIELDS:
        raise HTTPException(status_code=400, detail=f"Invalid sort field: {sort_field}")

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

@router.get("/{person_id}", response_model=Person, summary="Получить персону по UUID")
async def get_person(person_id: str):
    cache_key = f"person:{person_id}"
    cached = await get_cache(cache_key)
    if cached is not None:
        return cached

    body = {
        "query": {"term": {"uuid": person_id}},
        "size": 1
    }
    es_response = await search(INDEX_NAME, query=body)
    hits = es_response.get("hits", {}).get("hits", [])
    if not hits:
        raise HTTPException(status_code=404, detail="Person not found")

    result = hits[0]["_source"]
    await set_cache(cache_key, result, expire=300)
    return result
