from aiogram import F, Router, types

from src.app_setup import settings

router = Router()


@router.message(F.new_chat_members)
async def welcome_new_member(message: types.Message):

    for new_member in message.new_chat_members:
        if new_member.is_bot:
            continue

        await message.reply(
            text=f"Добро пожаловать, {new_member.full_name}!\n\n"
            f"Рады приветствовать тебя в нашем чате.\n\n"
            f"Чтобы получить доступ к эксклюзивным материалам, "
            f"напиши мне в личные сообщения: {settings.BOT_USERNAME}",
        )