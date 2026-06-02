from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message


class AdminMiddleware(BaseMiddleware):
    def __init__(self, admin_list: list):
        self.admin_list = set(admin_list)

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message ,
        data: Dict[str, Any],
    ) -> Any:
        if event.from_user.id in self.admin_list :
            return await handler(event, data)
        else:
            return None