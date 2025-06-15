import logging
from utils.elastic import es

logger = logging.getLogger(__name__)

INDEX_NAME = "persons"

ROLE_MAP = {
    "actors": "actor",
    "writers": "writer",
    "directors": "director"
}

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
                            "full_name": {"type": "text"},
                            "roles": {"type": "keyword"},
                        }
                    }
                }
            )
            logger.info(f"Created index {INDEX_NAME}")
    except Exception as e:
        logger.error(f"Error creating index {INDEX_NAME}: {e}")

async def index_persons(persons):
    actions = [
        {
            "_op_type": "index",
            "_index": INDEX_NAME,
            "_id": str(person["uuid"]),
            "_source": person
        }
        for person in persons
    ]
    try:
        response = await es.bulk(operations=actions)
        logger.info(f"Indexed {len(persons)} persons")
        return response
    except Exception as e:
        logger.error(f"Error bulk indexing persons: {e}")

async def etl_persons(all_films):
    await create_index()

    person_map = {}

    for film in all_films:
        for role_key in ("actors", "writers", "directors"):
            for person in film.get(role_key, []):
                uuid = person["uuid"]
                if uuid not in person_map:
                    person_map[uuid] = {
                        "uuid": uuid,
                        "full_name": person["full_name"],
                        "roles": []
                    }
                role = ROLE_MAP[role_key]
                if role not in person_map[uuid]["roles"]:
                    person_map[uuid]["roles"].append(role)

    if person_map:
        await index_persons(list(person_map.values()))
