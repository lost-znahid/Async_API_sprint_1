from utils.elastic import es

INDEX_NAME = "persons"

async def create_index():
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

async def index_persons(persons):
    for person in persons:
        await es.index(index=INDEX_NAME, id=person["uuid"], document=person)

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
                if role_key[:-1] not in person_map[uuid]["roles"]:
                    person_map[uuid]["roles"].append(role_key[:-1])  # actor, writer, director

    await index_persons(list(person_map.values()))
