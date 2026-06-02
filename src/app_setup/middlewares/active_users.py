import logging
from typing import Callable, Dict, Any, Awaitable, Iterable

from aiogram import BaseMiddleware
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from redis.asyncio import Redis

from src.databases.postgres.models.clients import ClientsORM


# Инициализируем логгер для этого модуля
logger = logging.getLogger(__name__)


class ActivationMiddleware(BaseMiddleware):
    def __init__(
        self,
        keyword: str,
        redis_client: Redis,
        admins: Iterable[int],
        cache_ttl: int = 86400,
    ) -> None:
        self.keyword = keyword.lower()
        self.redis = redis_client
        # O(1) сложность поиска вместо O(N) у списка
        self.admins = set(admins)
        # Вынесли время жизни кэша в конфигурацию мидлвари (по умолчанию 1 сутки)
        self.cache_ttl = cache_ttl

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        user_id = event.from_user.id

        # 1. Проверка на администратора (O(1) поиск по set)
        if user_id in self.admins:
            return await handler(event, data)

        redis_key = f"active_user:{user_id}"

        # 2. Безопасная проверка в кэше
        try:
            is_active_in_cache = await self.redis.get(redis_key)
            if is_active_in_cache:
                return await handler(event, data)
        except Exception as e:
            # Если Redis отвалился, логируем, но не кладем всего бота - идем проверять в БД
            logger.error(f"Redis connection error for user {user_id}: {e}")

        # 3. Получение сессии
        session: AsyncSession | None = data.get("session")
        if not session:
            logger.critical("Session is not found! Check DbSessionMiddleware order.")
            raise RuntimeError("Session is not found! Check DbSessionMiddleware order.")

        # 4. Безопасный запрос в БД
        try:
            user = await session.get(ClientsORM, user_id)
        except SQLAlchemyError as e:
            logger.error(f"Database error fetching user {user_id}: {e}")
            return None  # Прерываем цепочку при ошибке БД

        # 5. Пользователь найден и активен
        if user and user.is_active:
            try:
                await self.redis.set(redis_key, "1", ex=self.cache_ttl)
            except Exception as e:
                logger.error(f"Redis set error for user {user_id}: {e}")
            return await handler(event, data)

        # 6. Обработка кодового слова
        if event.text and event.text.lower() == self.keyword:
            try:
                if not user:
                    user = ClientsORM(telegram_id=user_id, is_active=True)
                    session.add(user)
                    logger.info(f"New user registered via keyword: {user_id}")
                else:
                    user.is_active = True
                    logger.info(f"Existing user activated via keyword: {user_id}")

                await session.commit()

                try:
                    # Раньше здесь не было аргумента ex! Кэш засорялся бы вечными ключами.
                    await self.redis.set(redis_key, "1", ex=self.cache_ttl)
                except Exception as e:
                    logger.error(
                        f"Redis set error after activation for user {user_id}: {e}"
                    )

                return await handler(event, data)
            except SQLAlchemyError as e:
                # В проде обязательно нужно откатывать сессию, если коммит вызвал ошибку
                await session.rollback()
                logger.error(f"Database error during user {user_id} activation: {e}")
                return None

        # Ни одно из условий не выполнилось — молча игнорируем
        return None
