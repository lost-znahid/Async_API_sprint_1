from elasticsearch import AsyncElasticsearch
from core.config import settings
import logging

logger = logging.getLogger(__name__)

es = AsyncElasticsearch(hosts=[settings.elastic_url])


async def search(index: str, query: dict, from_: int = 0, size: int = 10):
    try:
        response = await es.search(index=index, body=query, from_=from_, size=size)
        return response
    except Exception as e:
        logger.error(f"Elasticsearch search error: {e}")
        return {}
