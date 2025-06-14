from utils.elastic import es
import asyncio

INDEX_NAME = "genres"

async def create_index():
    exists = await es.indices.exists(index=INDEX_NAME)
    if not exists:
        await es.indices.create(
            index=INDEX_NAME,
            body={
                "mappings": {
                    "properties": {
                        "uuid": {"type": "keyword"},
                        "name": {"type": "text"},
                        "description": {"type": "text"},
                    }
                }
            }
        )

async def index_genres(genres):
    actions = [
        {
            "_index": INDEX_NAME,
            "_id": str(g["uuid"]),
            "_source": g
        } for g in genres
    ]
    for action in actions:
        await es.index(index=action["_index"], id=action["_id"], document=action["_source"])

async def etl_genres(all_films):
    await create_index()

    genre_map = {}
    for film in all_films:
        for genre in film.get("genres", []):
            genre_map[genre["uuid"]] = genre

    await index_genres(list(genre_map.values()))
