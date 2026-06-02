from aiogram import Router, types
from aiogram.filters.command import Command
from sqlalchemy.ext.asyncio import AsyncSession

from src.app_setup.config import settings
from src.app_setup.middlewares.admin_middleware import AdminMiddleware
from src.router.admin.crud_di import get_clients_di


admin_router = Router()
admin_router.message.middleware(AdminMiddleware(admin_list=[settings.ADMIN_ID]))


@admin_router.message(Command("clients"))
async def get_clients(message: types.Message, session: AsyncSession):
    clients_lst = await get_clients_di(session=session)
    
    if not clients_lst:
        await message.answer("Список клиентов пуст.")
        return

    response_lines = [
        f"{idx}. {client.full_name} - {client.phone_number}" 
        for idx, client in enumerate(clients_lst, start=1)
    ]
    response_text = "\n".join(response_lines)

    try:
         await message.answer(response_text)
    except Exception as e:

         await message.answer(f"Ошибка при отправке списка. Возможно, список слишком длинный: {e}")
