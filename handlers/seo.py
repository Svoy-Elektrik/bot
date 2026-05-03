from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from services.claude_service import generate_seo_article, rewrite_text, generate_meta

router = Router()


class SeoStates(StatesGroup):
    waiting_topic = State()
    waiting_keywords = State()
    waiting_rewrite_text = State()


# ─── /seo — Главное меню SEO ───
@router.message(Command("seo"))
async def seo_menu(message: Message):
    builder = InlineKeyboardBuilder()
    builder.button(text="✍️ Написать статью", callback_data="seo_article")
    builder.button(text="🔄 Рерайт текста", callback_data="seo_rewrite")
    builder.button(text="🏷️ Мета-теги", callback_data="seo_meta")
    builder.adjust(1)

    await message.answer(
        "📝 *SEO Мастер*\n\nЧто делаем?",
        parse_mode="Markdown",
        reply_markup=builder.as_markup()
    )


# ─── Написать статью ───
@router.callback_query(F.data == "seo_article")
async def seo_article_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("📌 Введи *тему статьи*:\n\nПример: _Как выбрать ноутбук для работы_", parse_mode="Markdown")
    await state.set_state(SeoStates.waiting_topic)
    await callback.answer()


@router.message(SeoStates.waiting_topic)
async def seo_article_topic(message: Message, state: FSMContext):
    await state.update_data(topic=message.text)
    await message.answer("🔑 Введи *ключевые слова* через запятую:\n\nПример: _ноутбук для работы, выбрать ноутбук, лучший ноутбук 2024_", parse_mode="Markdown")
    await state.set_state(SeoStates.waiting_keywords)


@router.message(SeoStates.waiting_keywords)
async def seo_article_generate(message: Message, state: FSMContext):
    data = await state.get_data()
    topic = data["topic"]
    keywords = message.text

    await message.answer("⏳ Генерирую SEO статью... Это займёт 20-40 секунд")

    try:
        article = await generate_seo_article(topic, keywords)
        # Разбиваем на части если слишком длинная (лимит Telegram 4096)
        if len(article) > 4000:
            parts = [article[i:i+4000] for i in range(0, len(article), 4000)]
            for i, part in enumerate(parts):
                await message.answer(f"📄 *Часть {i+1}/{len(parts)}*\n\n{part}", parse_mode="Markdown")
        else:
            await message.answer(article, parse_mode="Markdown")

        # Кнопки действий
        builder = InlineKeyboardBuilder()
        builder.button(text="🔍 Проверить на плагиат", callback_data="check_last_text")
        builder.button(text="🌐 Опубликовать в WP", callback_data="publish_last")
        builder.button(text="📢 Пост в канал", callback_data="post_to_channel")
        builder.adjust(1)

        await state.update_data(last_article=article, last_topic=topic)
        await message.answer("✅ Статья готова! Что дальше?", reply_markup=builder.as_markup())

    except Exception as e:
        await message.answer(f"❌ Ошибка генерации: {e}")

    await state.clear()


# ─── Рерайт текста ───
@router.callback_query(F.data == "seo_rewrite")
async def seo_rewrite_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("📋 Отправь текст для *рерайта и уникализации*:", parse_mode="Markdown")
    await state.set_state(SeoStates.waiting_rewrite_text)
    await callback.answer()


@router.message(SeoStates.waiting_rewrite_text)
async def seo_rewrite_do(message: Message, state: FSMContext):
    await message.answer("⏳ Делаю рерайт...")
    try:
        rewritten = await rewrite_text(message.text)
        await message.answer(f"✅ *Уникальный текст:*\n\n{rewritten}", parse_mode="Markdown")
        await state.update_data(last_article=rewritten)
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")
    await state.clear()


# ─── Мета-теги ───
@router.callback_query(F.data == "seo_meta")
async def seo_meta_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("📌 Введи тему и ключевые слова через `|`\n\nПример: `ноутбуки для работы | купить ноутбук, ноутбук цена`", parse_mode="Markdown")
    await state.set_state(SeoStates.waiting_topic)
    await callback.answer()
