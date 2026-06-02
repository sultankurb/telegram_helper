from aiogram import F, Router, types

router = Router()


@router.message(F.new_chat_members)
async def welcome_new_member(message: types.Message):

    for new_member in message.new_chat_members:
        if new_member.is_bot:
            continue

        await message.reply(
            text=f"Добро пожаловать, {new_member.full_name}!\n"
            f"Рады приветствовать тебя в нашем чате.",
        )
