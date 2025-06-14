from elasticsearch import AsyncElasticsearch
import os

ELASTIC_HOST = os.getenv("ELASTIC_HOST", "localhost")
ELASTIC_PORT = int(os.getenv("ELASTIC_PORT", 9200))

es = AsyncElasticsearch(hosts=[f"http://{ELASTIC_HOST}:{ELASTIC_PORT}"])

async def search(index: str, query: dict, from_: int = 0, size: int = 10):
    body = {
        "query": {
            "match_all": {}
        }
    }

    response = await es.search(index=index, body=body, from_=from_, size=size)
    return response
