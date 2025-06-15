import logging
from utils.elastic import es

logger = logging.getLogger(__name__)

INDEX_NAME = "genres"

async def create_index():
    try:
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
            logger.info(f"Index {INDEX_NAME} created")
    except Exception as e:
        logger.error(f"Error creating index {INDEX_NAME}: {e}")

async def index_genres(genres):
    actions = [
        {
            "_op_type": "index",
            "_index": INDEX_NAME,
            "_id": str(g["uuid"]),
            "_source": g
        }
        for g in genres
    ]
    try:
        response = await es.bulk(operations=actions)
        logger.info(f"Indexed {len(genres)} genres")
        return response
    except Exception as e:
        logger.error(f"Error bulk indexing genres: {e}")

async def etl_genres(all_films):
    await create_index()

    genre_map = {genre["uuid"]: genre for film in all_films for genre in film.get("genres", [])}
    genres = list(genre_map.values())

    if genres:
        await index_genres(genres)
