from aiogram.fsm.state import StatesGroup, State


class AdminFSM(StatesGroup):
    telegram_id = State()
