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
        keywords=["помощь", "admin", "админ", "help", "Купить интенсив"],
        redis_client=redis_client,
        admins=[settings.ADMIN_ID],
        cache_ttl=345600,
    )
)

STOP_KEYWORDS = {"/stop", "стоп", "stop", "✋ стоп", "✋ Стоп"}


@router.message(F.chat.id == settings.ADMIN_ID, F.reply_to_message)
async def handle_admin_reply(message: types.Message, bot: Bot, session: AsyncSession):
    """Forward admin replies to the original user if they are still active."""
    original_msg_id = message.reply_to_message.message_id
    user_id_str = await redis_client.get(f"msg_link:{original_msg_id}")

    if not user_id_str:
        await message.answer(
            "⚠️ Связь с этим сообщением не найдена или устарела в базе Redis."
        )
        return

    user_id = int(user_id_str)

    try:
        user = await session.get(ClientsORM, user_id)
    except Exception as e:
        logger.error(f"DB error checking user {user_id}: {e}")
        user = None

    if user and not user.is_active:
        await message.answer("Пользователь заблокирован/остановил диалог — сообщение не будет доставлено.")
        return

    try:
        await bot.copy_message(
            chat_id=user_id,
            from_chat_id=message.chat.id,
            message_id=message.message_id,
        )
        await message.react([types.ReactionTypeEmoji(emoji="👍")])
    except TelegramAPIError as e:
        await message.answer(f"❌ Ошибка отправки: {e}")


@router.message(F.chat.id == settings.ADMIN_ID, F.reply_to_message, F.text)
async def admin_stop_reply(message: types.Message, session: AsyncSession):
    """If admin replies with a stop keyword (as a reply), deactivate the user chat."""
    if message.text and message.text.lower() in STOP_KEYWORDS:
        original_msg_id = message.reply_to_message.message_id
        user_id_str = await redis_client.get(f"msg_link:{original_msg_id}")
        if not user_id_str:
            await message.answer("Связь с этим сообщением не найдена в Redis.")
            return

        user_id = int(user_id_str)
        try:
            user = await session.get(ClientsORM, user_id)
            if user:
                user.is_active = False
                await session.commit()
                await redis_client.delete(f"active_user:{user_id}")
                await message.answer(f"Диалог с пользователем {user_id} остановлен.")
                try:
                    await message.bot.send_message(
                        chat_id=user_id,
                        text="Администратор остановил диалог. Сообщения больше не будут доставлены.",
                    )
                except TelegramAPIError:
                    logger.warning(f"Не удалось уведомить пользователя {user_id} об остановке.")
            else:
                await message.answer("Пользователь не найден в БД.")
        except Exception as e:
            await session.rollback()
            logger.error(f"Ошибка при остановке диалога для {user_id}: {e}")
            await message.answer("Произошла ошибка при остановке диалога.")


@router.message(F.chat.type == "private", F.chat.id != settings.ADMIN_ID, F.text)
async def handle_client_messages(message: types.Message, bot: Bot, session: AsyncSession):
    """Handle client messages: forward to admin or process stop command."""
    if not message.text:
        return

    if message.text.lower() in STOP_KEYWORDS:
        user_id = message.from_user.id
        try:
            user = await session.get(ClientsORM, user_id)
            if user:
                user.is_active = False
                await session.commit()
            await redis_client.delete(f"active_user:{user_id}")
            await message.answer("Вы остановили диалог с администратором. Сообщения больше не будут отправляться.")
            try:
                await bot.send_message(
                    chat_id=settings.ADMIN_ID,
                    text=f"Пользователь {message.from_user.full_name} (ID: {user_id}) остановил диалог.",
                )
            except TelegramAPIError:
                logger.warning(f"Не удалось уведомить администратора о стопе от {user_id}.")
        except Exception as e:
            await session.rollback()
            logger.error(f"Ошибка при обработке стопа от {user_id}: {e}")
            await message.answer("Произошла ошибка при остановке диалога.")
        return

    try:
        info_msg = await bot.send_message(
            chat_id=settings.ADMIN_ID,
            text=f"📩 <b>От:</b> "
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
        await message.answer("Ваше сообщение было отправлено администратору. Ожидайте ответа.")

    except TelegramAPIError:
        await message.answer("Произошла ошибка при отправке.")