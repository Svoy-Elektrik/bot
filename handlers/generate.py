import logging

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from states import ArticleStates
from keyboards import output_kb
from services.claude import generate_article
from utils import split_for_telegram

router = Router()
log = logging.getLogger(__name__)


@router.message(ArticleStates.waiting_for_topic, F.text)
async def on_topic(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("lang", "ru")
    length = data.get("length", 3000)
    topic = message.text.strip()

    await message.answer("Генерирую статью…")

    try:
        article = generate_article(topic=topic, length=length, lang=lang)
    except Exception as e:
        log.exception("Generation failed")
        await message.answer(f"Ошибка генерации: {e}")
        return

    await state.update_data(article=article, topic=topic)

    for chunk in split_for_telegram(article):
        await message.answer(chunk)

    await message.answer("Куда выложить?", reply_markup=output_kb())
    await state.set_state(ArticleStates.choosing_output)
