import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from src.app_setup.middlewares.db_session import DbSessionMiddleware
from src.databases.postgres.connection import async_session
from src.app_setup.config import settings
from src.router.users.promo_router import router as promo_router
from src.router.users.register_router import router as register_router
from src.router.group.router import router as group_router


async def main():
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher()
    dp.message.outer_middleware(DbSessionMiddleware(session_pool=async_session))
    dp.include_router(register_router)
    dp.include_router(promo_router)
    dp.include_router(group_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен вручную.")
