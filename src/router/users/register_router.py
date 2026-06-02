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
from src.router.users.crud import insert_client

router = Router()


@router.message(Command("start"))
async def request_phone(message: Message):
    if message.from_user.id != settings.ADMIN_ID:
        contact_button = KeyboardButton(
            text="📱 Поделиться номером телефона", request_contact=True
        )
        keyboard = ReplyKeyboardMarkup(
            keyboard=[[contact_button]],
            resize_keyboard=True,
            one_time_keyboard=True,
        )
        await message.answer(
            text="Привет! "
                 "Для регистрации мне нужен ваш номер телефона. "
                 "Пожалуйста, нажмите кнопку ниже👇",
            reply_markup=keyboard,
        )
    else:
        await message.answer(text="Hello world admins")


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
            text=f"Спасибо, {message.contact.first_name}!",
            reply_markup=remove_keyboard,
        )
        await message.answer(
            text=""
        )
    except SQLAlchemyError as e:
        logging.error(msg=e)
