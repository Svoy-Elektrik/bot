from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from services.image_service import generate_image

router = Router()


class ImageStates(StatesGroup):
    waiting_prompt = State()


@router.message(Command("image"))
async def image_start(message: Message, state: FSMContext):
    await message.answer(
        "🎨 *Генератор изображений*\n\n"
        "Опиши что нужно нарисовать:\n\n"
        "_Пример: красивый закат над горами, для статьи о путешествиях, фотореализм_",
        parse_mode="Markdown"
    )
    await state.set_state(ImageStates.waiting_prompt)


@router.message(ImageStates.waiting_prompt)
async def image_generate(message: Message, state: FSMContext):
    await message.answer("⏳ Генерирую изображение...")

    try:
        img_bytes = await generate_image(message.text)
        if img_bytes:
            photo = BufferedInputFile(img_bytes, filename="seo_image.jpg")
            await message.answer_photo(
                photo=photo,
                caption=f"✅ Готово!\nПромпт: _{message.text}_",
                parse_mode="Markdown"
            )
        else:
            await message.answer(
                "❌ Не удалось сгенерировать изображение.\n"
                "Проверь наличие IDEOGRAM_API_KEY или OPENAI_API_KEY в настройках."
            )
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")

    await state.clear()
