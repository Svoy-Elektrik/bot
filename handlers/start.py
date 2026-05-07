from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from states import ArticleStates
from keyboards import lang_kb, length_kb

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "Привет! Я генерирую статьи через Claude.\n\nВыбери язык статьи:",
        reply_markup=lang_kb(),
    )
    await state.set_state(ArticleStates.choosing_lang)


@router.callback_query(F.data.startswith("lang:"), ArticleStates.choosing_lang)
async def on_lang(cb: CallbackQuery, state: FSMContext) -> None:
    lang = cb.data.split(":", 1)[1]
    await state.update_data(lang=lang)
    await cb.message.edit_text(
        "Выбери длину статьи (символов):",
        reply_markup=length_kb(),
    )
    await state.set_state(ArticleStates.choosing_length)
    await cb.answer()


@router.callback_query(F.data.startswith("len:"), ArticleStates.choosing_length)
async def on_length(cb: CallbackQuery, state: FSMContext) -> None:
    length = int(cb.data.split(":", 1)[1])
    await state.update_data(length=length)
    await cb.message.edit_text("Напиши тему статьи:")
    await state.set_state(ArticleStates.waiting_for_topic)
    await cb.answer()


@router.callback_query(F.data == "restart")
async def on_restart(cb: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await cb.message.answer(
        "Выбери язык статьи:",
        reply_markup=lang_kb(),
    )
    await state.set_state(ArticleStates.choosing_lang)
    await cb.answer()
