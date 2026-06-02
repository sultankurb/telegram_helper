from aiogram.fsm.state import State, StatesGroup


class AdminFSM(StatesGroup):
    telegram_id = State()


class MediaFSM(StatesGroup):
    media_url = State()
    media_comments = State()
