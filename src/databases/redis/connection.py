from redis.asyncio import from_url

from src.app_setup.config import settings

redis_client = from_url(
    url=settings.REDIS_URL,
    decode_responses=True,
    encoding="utf-8"
)