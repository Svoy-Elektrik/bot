from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from services.plagiat_service import check_plagiarism, improve_uniqueness

router = Router()


class PlagiatStates(StatesGroup):
    waiting_text = State()


def score_emoji(score: int) -> str:
    if score >= 80: return "✅"
    if score >= 60: return "⚠️"
    return "❌"


@router.message(Command("check"))
async def check_start(message: Message, state: FSMContext):
    await message.answer(
        "🔍 *Проверка и анализ текста*\n\n"
        "Отправь текст — Claude проверит:\n"
        "• Уникальность\n• Оригинальность\n• SEO качество\n• Человечность речи",
        parse_mode="Markdown"
    )
    await state.set_state(PlagiatStates.waiting_text)


@router.message(PlagiatStates.waiting_text)
async def check_text(message: Message, state: FSMContext):
    if len(message.text) < 100:
        await message.answer("❌ Текст слишком короткий. Минимум 100 символов.")
        return

    status_msg = await message.answer("⏳ Анализирую текст через Claude...")

    try:
        result = await check_plagiarism(message.text)

        if result.get("error"):
            await status_msg.edit_text(f"❌ Ошибка: {result['error']}")
            await state.clear()
            return

        u  = result["unique"]
        o  = result["originality"]
        s  = result["seo_quality"]
        h  = result["humanity"]

        report = (
            f"📊 *Результаты анализа текста*\n\n"
            f"{score_emoji(u)} Уникальность:   *{u}%*\n"
            f"{score_emoji(o)} Оригинальность: *{o}%*\n"
            f"{score_emoji(s)} SEO качество:   *{s}%*\n"
            f"{score_emoji(h)} Человечность:   *{h}%*\n"
        )

        if result.get("issues"):
            report += "\n⚠️ *Проблемы:*\n"
            for issue in result["issues"][:3]:
                report += f"• {issue}\n"

        if result.get("recommendations"):
            report += "\n💡 *Рекомендации:*\n"
            for rec in result["recommendations"][:3]:
                report += f"• {rec}\n"

        if result.get("verdict"):
            report += f"\n🤖 *Вердикт:* {result['verdict']}"

        builder = InlineKeyboardBuilder()
        if u < 80:
            builder.button(text="✨ Улучшить текст", callback_data="improve_text")
        builder.button(text="✍️ Написать новую статью", callback_data="seo_article")
        builder.adjust(1)

        await state.update_data(last_text=message.text, last_score=u)
        await status_msg.edit_text(report, parse_mode="Markdown", reply_markup=builder.as_markup())

    except Exception as e:
        await status_msg.edit_text(f"❌ Ошибка: {e}")

    await state.clear()


@router.callback_query(F.data == "improve_text")
async def improve_text(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    text = data.get("last_text")
    score = data.get("last_score", 0)

    if not text:
        await callback.message.answer("❌ Нет текста для улучшения.")
        await callback.answer()
        return

    await callback.message.answer("⏳ Улучшаю текст...")
    improved = await improve_uniqueness(text, score)

    if len(improved) > 4000:
        parts = [improved[i:i+4000] for i in range(0, len(improved), 4000)]
        for i, part in enumerate(parts):
            await callback.message.answer(f"✨ *Улучшенный текст ({i+1}/{len(parts)}):*\n\n{part}", parse_mode="Markdown")
    else:
        await callback.message.answer(f"✨ *Улучшенный текст:*\n\n{improved}", parse_mode="Markdown")

    await callback.answer()


@router.callback_query(F.data == "check_last_text")
async def check_last(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    article = data.get("last_article")

    if not article:
        await callback.message.answer("❌ Нет текста. Сначала сгенерируй статью.")
        await callback.answer()
        return

    await callback.message.answer("⏳ Анализирую статью...")
    result = await check_plagiarism(article)

    if result.get("error"):
        await callback.message.answer(f"❌ {result['error']}")
    else:
        u = result["unique"]
        await callback.message.answer(
            f"{score_emoji(u)} *Анализ статьи:*\n\n"
            f"Уникальность: *{u}%*\n"
            f"SEO качество: *{result['seo_quality']}%*\n"
            f"Человечность: *{result['humanity']}%*\n\n"
            f"_{result.get('verdict', '')}_",
            parse_mode="Markdown"
        )
    await callback.answer()
