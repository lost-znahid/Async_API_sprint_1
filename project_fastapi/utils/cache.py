from redis.asyncio import from_url
from redis.exceptions import RedisError
import os
import json

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

redis = from_url(f"redis://{REDIS_HOST}:{REDIS_PORT}", encoding="utf-8", decode_responses=True)

async def get_cache(key: str):
    try:
        data = await redis.get(key)
        if data:
            return json.loads(data)
    except RedisError:
        # Логирование ошибки, например
        pass
    return None

async def set_cache(key: str, value, expire: int = 60):
    try:
        data = json.dumps(value)
        await redis.set(key, data, ex=expire)
    except RedisError:
        # Логирование ошибки, например
        pass

