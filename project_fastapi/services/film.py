from utils.elastic import es

INDEX_NAME = "films"

async def create_index():
    exists = await es.indices.exists(index=INDEX_NAME)
    if not exists:
        await es.indices.create(
            index=INDEX_NAME,
            body={
                "mappings": {
                    "properties": {
                        "uuid": {"type": "keyword"},
                        "title": {"type": "text"},
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
        )

async def index_films(films):
    for film in films:
        await es.index(index=INDEX_NAME, id=film["uuid"], document=film)
