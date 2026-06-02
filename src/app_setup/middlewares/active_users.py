import logging
from typing import Any, Awaitable, Callable, Dict, Iterable

from aiogram import BaseMiddleware
from aiogram.types import Message
from redis.asyncio import Redis
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.databases.postgres.models.clients import ClientsORM

logger = logging.getLogger(__name__)


class ActivationMiddleware(BaseMiddleware):
    def __init__(
        self,
        keywords: list[str],
        redis_client: Redis,
        admins: Iterable[int],
        cache_ttl: int = 86400,
    ) -> None:
        self.keywords = set(keywords)
        self.redis = redis_client
        self.admins = set(admins)
        self.cache_ttl = cache_ttl

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        user_id = event.from_user.id

        if user_id in self.admins:
            return await handler(event, data)

        redis_key = f"active_user:{user_id}"

        try:
            is_active_in_cache = await self.redis.get(redis_key)
            if is_active_in_cache:
                return await handler(event, data)
        except Exception as e:
            logger.error(f"Redis connection error for user {user_id}: {e}")

        session: AsyncSession | None = data.get("session")
        if not session:
            logger.critical(
                "Session is not found! Check DbSessionMiddleware order."
            )
            raise RuntimeError(
                "Session is not found! Check DbSessionMiddleware order."
            )

        try:
            user = await session.get(ClientsORM, user_id)
        except SQLAlchemyError as e:
            logger.error(f"Database error fetching user {user_id}: {e}")
            return None

        if user and user.is_active:
            try:
                await self.redis.set(redis_key, "1", ex=self.cache_ttl)
            except Exception as e:
                logger.error(f"Redis set error for user {user_id}: {e}")
            return await handler(event, data)

        if event.text and event.text.lower() in self.keywords:
            try:
                if not user:
                    user = ClientsORM(telegram_id=user_id, is_active=True)
                    session.add(user)
                    logger.info(f"New user registered via keyword: {user_id}")
                else:
                    user.is_active = True
                    logger.info(
                        f"Existing user activated via keyword: {user_id}"
                    )

                await session.commit()

                try:
                    await self.redis.set(redis_key, "1", ex=self.cache_ttl)
                except Exception as e:
                    logger.error(
                        msg=f"Redis set error after activation for user"
                            f" {user_id}: {e}"
                    )

                return await handler(event, data)
            except SQLAlchemyError as e:
                await session.rollback()
                logger.error(
                    f"Database error during user {user_id} activation: {e}"
                )
                return None

        return None
