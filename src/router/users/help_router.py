from aiogram import Bot, F, Router, types
from aiogram.exceptions import TelegramAPIError
from sqlalchemy.ext.asyncio import AsyncSession

import logging

from src.app_setup.config import settings
from src.app_setup.middlewares.active_users import ActivationMiddleware
from src.databases.redis.connection import redis_client
from src.databases.postgres.models.clients import ClientsORM

logger = logging.getLogger(__name__)

router = Router()
router.message.middleware(
    ActivationMiddleware(
        keywords=["помощь", "admin", "админ", "help", "продлить"],
        redis_client=redis_client,
        admins=[settings.ADMIN_ID],
        cache_ttl=345600,
    )
)

STOP_KEYWORDS = {"/stop", "стоп", "stop", "✋ стоп", "✋ Стоп"}


@router.message(F.chat.id == settings.ADMIN_ID, F.reply_to_message)
async def handle_admin_reply(message: types.Message, bot: Bot, session: AsyncSession):
    """Forward admin replies to the original user if they are still active."""
    # Обработка команды стоп от админа
    text = message.text or message.caption
    if text and text.lower() in STOP_KEYWORDS:
        original_msg_id = message.reply_to_message.message_id
        user_id_str = await redis_client.get(f"msg_link:{original_msg_id}")
        if not user_id_str:
            await message.answer("Бұл хабарламамен байланыс Redis-те табылмады.")
            return

        user_id = int(user_id_str)
        try:
            user = await session.get(ClientsORM, user_id)
            if user:
                user.is_active = False
                await session.commit()
                await redis_client.delete(f"active_user:{user_id}")
                await message.answer(f"Пайдаланушымен {user_id} диалог тоқтатылды.")
                try:
                    await bot.send_message(
                        chat_id=user_id,
                        text="Әкімші диалогты тоқтатты. Хабарламалар бұдан былай жеткізілмейді.",
                    )
                except TelegramAPIError:
                    logger.warning(f"Пайдаланушыға {user_id} тоқтату туралы хабарлау мүмкін болмады.")
            else:
                await message.answer("Пайдаланушы ДҚ-да табылмады.")
        except Exception as e:
            await session.rollback()
            logger.error(f"{user_id} үшін диалогты тоқтату кезіндегі қате: {e}")
            await message.answer("Диалогты тоқтату кезінде қате пайда болды.")
        return

    # Иначе пересылаем сообщение пользователю
    original_msg_id = message.reply_to_message.message_id
    user_id_str = await redis_client.get(f"msg_link:{original_msg_id}")

    if not user_id_str:
        await message.answer(
            "⚠️ Бұл хабарламамен байланыс табылмады немесе Redis дерекқорында ескірген."
        )
        return

    user_id = int(user_id_str)

    try:
        user = await session.get(ClientsORM, user_id)
    except Exception as e:
        logger.error(f"DB error checking user {user_id}: {e}")
        user = None

    if user and not user.is_active:
        await message.answer("Пайдаланушы блоктаулы/диалогты тоқтатты — хабарлама жеткізілмейді.")
        return

    try:
        await bot.copy_message(
            chat_id=user_id,
            from_chat_id=message.chat.id,
            message_id=message.message_id,
        )
        await message.react([types.ReactionTypeEmoji(emoji="👍")])
    except TelegramAPIError as e:
        await message.answer(f"❌ Жіберу қатесі: {e}")


@router.message(F.chat.type == "private", F.chat.id != settings.ADMIN_ID)
async def handle_client_messages(message: types.Message, bot: Bot, session: AsyncSession):
    """Handle client messages: forward to admin or process stop command."""
    text = message.text or message.caption

    if text and text.lower() in STOP_KEYWORDS:
        user_id = message.from_user.id
        try:
            user = await session.get(ClientsORM, user_id)
            if user:
                user.is_active = False
                await session.commit()
            await redis_client.delete(f"active_user:{user_id}")
            await message.answer("Сіз әкімшімен диалогты тоқтаттыңыз. Хабарламалар бұдан былай жіберілмейді.")
            try:
                await bot.send_message(
                    chat_id=settings.ADMIN_ID,
                    text=f"Пайдаланушы {message.from_user.full_name} (ID: {user_id}) диалогты тоқтатты.",
                )
            except TelegramAPIError:
                logger.warning(f"Әкімшіге {user_id} тоқтатуы туралы хабарлау мүмкін болмады.")
        except Exception as e:
            await session.rollback()
            logger.error(f"{user_id} тоқтатуын өңдеу кезіндегі қате: {e}")
            await message.answer("Диалогты тоқтату кезінде қате пайда болды.")
        return

    try:
        info_msg = await bot.send_message(
            chat_id=settings.ADMIN_ID,
            text=f"📩 <b>Кімнен:</b> "
                 f"{message.from_user.full_name}\n"
                 f"<b>ID:</b> "
                 f"<code>{message.from_user.id}</code>",
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
            f"msg_link:{copied_msg.message_id}",
            message.from_user.id,
            ex=604800,
        )
        await message.answer("Сіздің хабарламаңыз әкімшіге жіберілді. Жауап күтіңіз. Диалокты токтату ушин стоп жазинг")

    except TelegramAPIError:
        await message.answer("Жіберу кезінде қате пайда болды.")
