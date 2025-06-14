from redis.asyncio import from_url
import os
import json

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

redis = from_url(f"redis://{REDIS_HOST}:{REDIS_PORT}", encoding="utf-8", decode_responses=True)

async def get_cache(key: str):
    data = await redis.get(key)
    if data:
        return json.loads(data)
    return None

async def set_cache(key: str, value, expire: int = 60):
    data = json.dumps(value)
    await redis.set(key, data, ex=expire)
