import logging

from aiogram import F, Router, types
from aiogram.filters import StateFilter
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from src.app_setup import AdminMiddleware, settings
from src.router.admin.crud_di import get_clients_di
from src.router.admin.fms import MediaFSM

admin_router = Router()
admin_router.message.middleware(
    AdminMiddleware(admin_list=[settings.ADMIN_ID])
)
logger = logging.getLogger(__name__)


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
        await message.answer(
            f"Ошибка при отправке списка."
            f" Возможно, список слишком длинный: {e}"
        )


@admin_router.message(StateFilter(None), Command("add-media"))
async def new_media(message: types.Message, state: FSMContext):
    await message.answer(text="Отправте мне ваше видео")
    await state.set_state(MediaFSM.media_url)


@admin_router.message(MediaFSM.media_url, F.video)
async def get_video(message: types.Message, state: FSMContext):
    video_id = message.video.file_id
    await state.update_data(media_url=video_id)
    await message.answer(text="Оставте небольшое описание видео")


@admin_router.message(MediaFSM.media_comments, F.text)
async def add_description(message: types.Message, state: FSMContext):
    await state.update_data(media_comments=message.text)
    try:
        data = await state.get_data()
        await state.clear()
        await message.answer(text="Успошено добавлен")
        logger.info(msg=data)
    except Exception as e:
        await message.answer(text=f"Критическая ошибка {e}")
        logging.error(msg=e)
