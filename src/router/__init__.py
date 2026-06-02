from aiogram import F, Router, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from src.app_setup.middlewares.db_session import DbSessionMiddleware
from src.databases.postgres.connection import async_session
from src.router.admin.admin import admin_router
from src.router.group.router import router as group_router
from src.router.users.promo_router import router as promo_router
from src.router.users.register_router import router as register_router

main_router = Router()
main_router.include_routers(
    admin_router, group_router, promo_router, register_router
)
main_router.message.outer_middleware(
    DbSessionMiddleware(session_pool=async_session)
)

@main_router.message(StateFilter("*"), F.text == "отмена")
async def cancel(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Все действия отменены")
