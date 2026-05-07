import logging

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from states import ArticleStates
from services.wordpress import publish_to_wordpress, WordPressNotConfigured
from services.telegram_publish import publish_to_telegram, TelegramChannelNotConfigured

router = Router()
log = logging.getLogger(__name__)


@router.callback_query(F.data == "out:wp", ArticleStates.choosing_output)
async def out_wp(cb: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    article = data.get("article", "")
    topic = data.get("topic", "Article")
    try:
        url = publish_to_wordpress(title=topic, content=article)
        await cb.message.answer(f"Опубликовано в WordPress: {url}")
    except WordPressNotConfigured:
        await cb.message.answer(
            "WordPress не настроен. Задай WP_URL, WP_USER, WP_APP_PASSWORD в переменных окружения."
        )
    except Exception as e:
        log.exception("WordPress publish failed")
        await cb.message.answer(f"Ошибка WordPress: {e}")
    await cb.answer()


@router.callback_query(F.data == "out:tg", ArticleStates.choosing_output)
async def out_tg(cb: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    article = data.get("article", "")
    try:
        await publish_to_telegram(cb.bot, article)
        await cb.message.answer("Опубликовано в Telegram-канал.")
    except TelegramChannelNotConfigured:
        await cb.message.answer(
            "Telegram-канал не настроен. Задай TG_CHANNEL_ID и сделай бота админом канала."
        )
    except Exception as e:
        log.exception("Telegram publish failed")
        await cb.message.answer(f"Ошибка Telegram: {e}")
    await cb.answer()


@router.callback_query(F.data == "out:copy", ArticleStates.choosing_output)
async def out_copy(cb: CallbackQuery, state: FSMContext) -> None:
    await cb.message.answer(
        "Текст уже отправлен сообщениями выше — нажми и удерживай его, чтобы скопировать."
    )
    await cb.answer()
