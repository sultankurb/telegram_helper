from aiogram import Router, types, F
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext

from src.app_setup.config import settings
from src.app_setup.middlewares.admin_middleware import AdminMiddleware
from src.router.admin.fms import AdminFSM

admin_router = Router()
admin_router.message.middleware(AdminMiddleware(
    admin_list=[settings.ADMIN_ID]
))


@admin_router.message(Command("clients"))
async def get_clients(message: types.Message):
    await message.answer(text="Clients")


@admin_router.message(F.text.lower() == "add admin")
async def new_admin(message: types.Message, state: FSMContext):
    await message.answer(text="Send me new admins ID")
    await state.set_state(AdminFSM.telegram_id)



@admin_router.message(AdminFSM.telegram_id, F.text.isdigit())
async def add_new_admin(message: types.Message, state: FSMContext):
    data = await state.set_data(telegram_id=message.text)