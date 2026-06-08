import logging

from aiogram import F, Router
from aiogram.filters.command import Command
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.app_setup.config import settings
from src.router.users.crud import (
    insert_client,
    get_recent_media,
    get_client_by_telegram_id
)
from src.router.admin.keyboards import admin_keyboard

router = Router()
logger = logging.getLogger(__name__)


async def send_media_and_offer(message: Message, session: AsyncSession):
    """Отправляет медиафайлы и кнопку для покупки интенсива."""
    media_files = await get_recent_media(session=session, limit=5)
    if not media_files:
        logger.warning("Нет медиафайлов для отправки.")
        await message.answer("Өкінішке орай, қазір қолжетімді медиафайлдар жоқ.")
        return

    logger.info(f"Найдено {len(media_files)} медиафайлов для отправки.")
    for media in media_files:
        try:
            await message.answer_video(
                video=media.media_url,
                caption=media.media_comments
            )
            logger.info(f"Отправлено видео с file_id: {media.media_url}")
        except Exception as e:
            logger.error(f"Ошибка при отправке видео с file_id: {media.media_url}. Ошибка: {e}")
            await message.answer("Бейнелердің бірін жіберу мүмкін болмады. Кейінірек қайталап көріңіз.")

    await message.answer(
        text="Толық интенсивті алу үшін төмендегі түймені басыңыз",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Продлить")]],
            resize_keyboard=True,
        )
    )


@router.message(Command("start"))
async def request_phone(message: Message, session: AsyncSession):
    if message.from_user.id == settings.ADMIN_ID:
        await message.answer(
            text="Добро пожаловать, администратор!"
        )
        return

    client = await get_client_by_telegram_id(session, message.from_user.id)
    if client:
        await send_media_and_offer(message, session)
    else:
        contact_button = KeyboardButton(
            text="📱 Телефон нөмірімен бөлісу", request_contact=True
        )
        keyboard = ReplyKeyboardMarkup(
            keyboard=[[contact_button]],
            resize_keyboard=True,
            one_time_keyboard=True,
        )
        await message.answer(
            text="Сәлем! "
                 "Тіркелу үшін маған сіздің телефон нөміріңіз қажет. "
                 "Төмендегі түймені басыңыз👇",
            reply_markup=keyboard,
        )


@router.message(Command("admin"))
async def admin_panel(message: Message):
    if message.from_user.id == settings.ADMIN_ID:
        await message.answer("Панель администратора", reply_markup=admin_keyboard)


@router.message(F.contact)
async def get_contact(message: Message, session: AsyncSession):
    remove_keyboard = ReplyKeyboardRemove()
    try:
        await insert_client(
            session=session,
            data={
                "is_active": False,
                "full_name": message.from_user.first_name,
                "telegram_id": message.from_user.id,
                "phone_number": message.contact.phone_number,
            },
        )
        await message.answer(
            text=f"Рақмет, {message.contact.first_name}!",
            reply_markup=remove_keyboard,
        )

        await send_media_and_offer(message, session)

    except SQLAlchemyError as e:
        logging.error(msg=e)
        await message.answer("Тіркелу кезінде қате пайда болды. Кейінірек қайталап көріңіз.")