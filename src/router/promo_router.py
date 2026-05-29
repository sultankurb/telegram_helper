from aiogram import Bot, F, Router, types
from aiogram.filters import CommandStart
from aiogram.exceptions import TelegramAPIError
from redis.asyncio import Redis

from src.app_setup.config import settings

router = Router()

redis_client = Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    password=settings.REDIS_PASSWORD,
    username=settings.REDIS_USERNAME,
    decode_responses=True,
)


@router.message(CommandStart())
async def cmd_start(message: types.Message):
    if message.from_user.id == settings.ADMIN_ID:
        await message.answer("👋 <b>Привет, Админ!</b> Режим с Redis активирован.")
    else:
        await message.answer("Здравствуйте! Напишите ваш вопрос, и мы вам ответим.")


@router.message(F.chat.id == settings.ADMIN_ID, F.reply_to_message)
async def handle_admin_reply(message: types.Message, bot: Bot):
    original_msg_id = message.reply_to_message.message_id
    user_id_str = await redis_client.get(f"msg_link:{original_msg_id}")

    if user_id_str:
        user_id = int(user_id_str)
        try:
            await bot.copy_message(
                chat_id=user_id,
                from_chat_id=message.chat.id,
                message_id=message.message_id,
            )
            await message.react([types.ReactionTypeEmoji(emoji="👍")])
        except TelegramAPIError as e:
            await message.answer(f"❌ Ошибка отправки: {e}")
    else:
        await message.answer(
            "⚠️ Связь с этим сообщением не найдена или устарела в базе Redis."
        )


@router.message(F.chat.type == "private", F.chat.id != settings.ADMIN_ID)
async def handle_client_message(message: types.Message, bot: Bot):
    try:
        info_msg = await bot.send_message(
            chat_id=settings.ADMIN_ID,
            text=f"📩 <b>От:</b> {message.from_user.full_name}\n<b>ID:</b> <code>{message.from_user.id}</code>",
        )

        copied_msg = await bot.copy_message(
            chat_id=settings.ADMIN_ID,
            from_chat_id=message.chat.id,
            message_id=message.message_id,
        )
        await redis_client.set(
            f"msg_link:{info_msg.message_id}", message.from_user.id, ex=604800
        )
        await redis_client.set(
            f"msg_link:{copied_msg.message_id}", message.from_user.id, ex=604800
        )

    except TelegramAPIError:
        await message.answer("Произошла ошибка при отправке.")
