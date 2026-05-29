import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, F, Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message

from src.app_setup.config import settings
from src.router.promo_router import router 


dp = Dispatcher()
bot = Bot(
    token=settings.BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)


@dp.message(Command("start"))
async def request_phone(message: Message):

    contact_button = KeyboardButton(text="📱 Поделиться контактом", request_contact=True)
    

    keyboard = ReplyKeyboardMarkup(
        keyboard=[[contact_button]],
        resize_keyboard=True,
        one_time_keyboard=True     
    )

    await message.reply(
        "Пожалуйста, поделитесь своим номером телефона для связи с администратором. "
        "Для этого нажмите кнопку ниже 👇",
        reply_markup=keyboard
    )

@dp.message(F.contact)
async def handle_contact(message: Message):

    contact = message.contact
    phone_number = contact.phone_number
    first_name = contact.first_name
    

    await message.reply(
        f"Спасибо! Ваш номер ({phone_number}) успешно сохранен.",
        reply_markup=ReplyKeyboardRemove()
    )

    text_for_admin = (
        f"🆕 <b>Новый контакт!</b>\n"
        f"Имя: {first_name}\n"
        f"Username: @{message.from_user.username}\n"
        f"Номер телефона: <code>{phone_number}</code>"
    )
    await bot.send_message(settings.ADMIN_ID, text_for_admin, parse_mode="HTML")

dp.include_router(router)

async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
