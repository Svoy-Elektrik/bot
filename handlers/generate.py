from aiogram import Router, F
from aiogram.types import Message
from services.claude import generate_text

router = Router()

@router.message(F.text)
async def handle_text(message: Message):
    user_text = message.text

    result = generate_text(f"Сгенерируй текст по задаче: {user_text}", 1500)

    await message.answer(result)

    await message.answer(
        "Куда отправить?\n"
        "1 - Telegram\n"
        "2 - WordPress\n"
        "3 - Скачать файл"
    )
