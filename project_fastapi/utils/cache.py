from redis.asyncio import from_url
from redis.exceptions import RedisError
from core.config import settings
import json
import logging

logger = logging.getLogger(__name__)

# Создание клиента Redis через URL из настроек
redis = from_url(settings.redis_url, encoding="utf-8", decode_responses=True)


async def get_cache(key: str):
    try:
        data = await redis.get(key)
        if data:
            return json.loads(data)
    except RedisError as e:
        logger.error(f"Redis error during get: {e}")
    return None


async def set_cache(key: str, value, expire: int = 60):
    try:
        data = json.dumps(value)
        await redis.set(key, data, ex=expire)
    except RedisError as e:
        logger.error(f"Redis error during set: {e}")
