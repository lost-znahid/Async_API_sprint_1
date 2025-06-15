import logging
from core.config import settings
from elasticsearch.helpers import async_bulk
from project_fastapi.models.film import Film
from typing import List, Optional
from utils.elastic import es, search
from utils.cache import get_cache, set_cache

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

INDEX_NAME = "films"

# Конфигурация индекса
index_body = {
    "mappings": {
        "properties": {
            "uuid": {"type": "keyword"},
            "title": {
                "type": "text",
                "fields": {"raw": {"type": "keyword"}}
            },
            "description": {"type": "text"},
            "imdb_rating": {"type": "float"},
            "genres": {
                "type": "nested",
                "properties": {
                    "uuid": {"type": "keyword"},
                    "name": {"type": "text"},
                    "description": {"type": "text"},
                }
            },
            "actors": {
                "type": "nested",
                "properties": {
                    "uuid": {"type": "keyword"},
                    "full_name": {"type": "text"},
                }
            },
            "writers": {
                "type": "nested",
                "properties": {
                    "uuid": {"type": "keyword"},
                    "full_name": {"type": "text"},
                }
            },
            "directors": {
                "type": "nested",
                "properties": {
                    "uuid": {"type": "keyword"},
                    "full_name": {"type": "text"},
                }
            }
        }
    }
}


async def create_index() -> None:
    try:
        if not await es.indices.exists(index=INDEX_NAME):
            await es.indices.create(index=INDEX_NAME, body=index_body)
            logger.info(f"Index '{INDEX_NAME}' created.")
        else:
            logger.info(f"Index '{INDEX_NAME}' already exists.")
    except Exception as e:
        logger.error(f"Error creating index '{INDEX_NAME}': {e}")

async def index_films(films: List[Film]) -> None:
    actions = [
        {
            "_index": INDEX_NAME,
            "_id": film["uuid"],
            "_source": film
        }
        for film in films
    ]
    try:
        await async_bulk(es, actions)
        logger.info(f"Indexed {len(films)} films")
    except Exception as e:
        logger.error(f"Bulk indexing failed: {e}")



async def get_films_list(page_number: int, page_size: int, sort: str) -> List[dict]:
    cache_key = f"films:{page_number}:{page_size}:{sort}"
    cached = await get_cache(cache_key)
    if cached:
        return cached

    sort_field = sort.lstrip("-")
    sort_order = "desc" if sort.startswith("-") else "asc"

    body = {
        "query": {"match_all": {}},
        "from": (page_number - 1) * page_size,
        "size": page_size,
        "sort": [{sort_field: {"order": sort_order}}]
    }

    try:
        es_response = await search(INDEX_NAME, query=body)
        hits = es_response["hits"]["hits"]
        result = [hit["_source"] for hit in hits]
        await set_cache(cache_key, result, expire=120)
        return result
    except Exception as e:
        logger.error(f"Failed to fetch films list: {e}")
        return []


async def get_film_by_id(film_id: str) -> Optional[dict]:
    cache_key = f"film:{film_id}"
    cached = await get_cache(cache_key)
    if cached:
        return cached

    body = {
        "query": {"term": {"uuid": film_id}},
        "size": 1
    }

    try:
        es_response = await search(INDEX_NAME, query=body)
        hits = es_response["hits"]["hits"]
        if not hits:
            return None
        result = hits[0]["_source"]
        await set_cache(cache_key, result, expire=300)
        return result
    except Exception as e:
        logger.error(f"Failed to fetch film by id: {e}")
        return None
