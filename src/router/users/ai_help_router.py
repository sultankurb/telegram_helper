from aiogram import F, Router, types

from src.app_setup.config import settings
from src.app_setup.middlewares.active_users import ActivationMiddleware
from src.databases.redis.connection import redis_client
from src.router.users.ai_di import make_response

router = Router()
router.message.middleware(
    ActivationMiddleware(
        keywords=["консультация", "konsultaciya", "konsultacija"],
        redis_client=redis_client,
        admins=[settings.ADMIN_ID],
        cache_ttl=345600,
    )
)

@router.message()
async def debug(message: types.Message):
    await message.answer(
        text="Этот режим тестовы.\n"
        "При любых ошибках обрашайтесь\n"
        "вот сюда: https://t.me/surutan666"
    )

@router.message(F.text)
async def get_answer_from_ai(message: types.Message):
    try:
        question = str(message.text)
        answer = await make_response(question=question)
        await message.answer(text=str(answer))

    except TypeError:
        await message.answer("Nice try!")
