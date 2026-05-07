from aiogram.fsm.state import State, StatesGroup


class ArticleStates(StatesGroup):
    choosing_lang = State()
    choosing_length = State()
    waiting_for_topic = State()
    choosing_output = State()
