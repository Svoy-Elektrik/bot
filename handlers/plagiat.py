from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from services.plagiat_service import check_plagiarism

router = Router()

class PlagiatStates(StatesGroup):
    waiting_text = State()

@router.message(Command("check"))
async def check_start(message: Message, state: FSMContext):
    await message.answer(
        "🔍 *Проверка на плагиат*\n\n"
        "Отправь текст для проверки уникальности.\n"
        "⏱ Проверка занимает 1-2 минуты.",
        parse_mode="Markdown"
    )
    await state.set_state(PlagiatStates.waiting_text)

@router.message(PlagiatStates.waiting_text)
async def check_text(message: Message, state: FSMContext):
    if len(message.text) < 100:
        await message.answer("❌ Текст слишком короткий. Минимум 100 символов.")
        return
    status_msg = await message.answer("⏳ Отправляю текст на проверку Text.ru...\nЭто займёт 1-2 минуты.")
    try:
        result = await check_plagiarism(message.text)
        if result.get("error"):
            await status_msg.edit_text(f"❌ Ошибка: {result['error']}")
        else:
            unique = result["unique"]
            emoji = "✅" if unique >= 80 else ("⚠️" if unique >= 60 else "❌")
            text = (
                f"{emoji} *Результат проверки:*\n\n"
