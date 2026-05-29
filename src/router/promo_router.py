import types

from aiogram import Router, F, Bot
from aiogram.types import Message

from src.app_setup.config import settings

router = Router()

user_admin_map = {}
bot = Bot(token=settings.BOT_TOKEN)

KEYWORDS = ["админ", "связь", "помощь", "поддержка"]

def contains_keyword(text: str) -> bool:

    if not text:
        return False
    text_lower = text.lower()
    return any(word in text_lower for word in KEYWORDS)


@router.message(F.text, F.from_user.id != settings.ADMIN_ID)
async def handle_user_message(message: Message):
    if not contains_keyword(message.text):
        return 

    user_id = message.from_user.id
    username = f"@{message.from_user.username}" if message.from_user.username else f"ID: {user_id}"
    
    text_for_admin = f"🔔 Обращение от {username}:\n\n{message.text}"
    
    
    msg_to_admin = await bot.send_message(settings.ADMIN_ID, text_for_admin)
    
    user_admin_map[msg_to_admin.message_id] = user_id
    
    
    await message.reply("Ваше сообщение передано администратору. Пожалуйста, ожидайте ответа.")



@router.message(F.from_user.id == settings.ADMIN_ID, F.reply_to_message)
async def handle_admin_reply(message: Message):

    original_msg_id = message.reply_to_message.message_id
    

    if original_msg_id in user_admin_map:
        user_id = user_admin_map[original_msg_id]
        
        try:

            await bot.send_message(user_id, f"👨‍💻 Ответ от администратора:\n\n{message.text}")

            await message.reply("Ответ успешно отправлен пользователю!")
        except Exception as e:

            await message.reply(f"Не удалось отправить сообщение пользователю. Ошибка: {e}")
    else:
        await message.reply("Ошибка: не удалось найти пользователя для этого сообщения (возможно, бот был перезапущен).")
