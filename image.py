from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from services.image_service import generate_image, generate_og_image, generate_article_image

router = Router()


class ImageStates(StatesGroup):
    choosing_type = State()
    choosing_style = State()
    waiting_prompt = State()


@router.message(Command("image"))
async def image_menu(message: Message, state: FSMContext):
    builder = InlineKeyboardBuilder()
    builder.button(text="📰 Для статьи (16:9)", callback_data="img_type_article")
    builder.button(text="📱 OG / Соцсети",      callback_data="img_type_og")
    builder.button(text="✨ Свой промт",         callback_data="img_type_free")
    builder.adjust(1)

    await message.answer(
        "🎨 *Генератор изображений*\n\n"
        "Через Pollinations.ai — бесплатно, без ключей\n\n"
        "Выбери тип изображения:",
        parse_mode="Markdown",
        reply_markup=builder.as_markup()
    )


# ─── Для статьи — выбор стиля ───
@router.callback_query(F.data == "img_type_article")
async def img_article_style(callback: CallbackQuery, state: FSMContext):
    builder = InlineKeyboardBuilder()
    builder.button(text="📷 Фото реализм",    callback_data="img_style_photo")
    builder.button(text="🎨 Флэт иллюстрация", callback_data="img_style_flat")
    builder.button(text="🔮 3D рендер",        callback_data="img_style_3d")
    builder.button(text="🖌 Акварель",         callback_data="img_style_watercolor")
    builder.adjust(2)

    await state.update_data(img_type="article")
    await callback.message.answer("Выбери стиль:", reply_markup=builder.as_markup())
    await callback.answer()


# ─── OG изображение — выбор стиля ───
@router.callback_query(F.data == "img_type_og")
async def img_og_style(callback: CallbackQuery, state: FSMContext):
    builder = InlineKeyboardBuilder()
    builder.button(text="💼 Деловой",    callback_data="img_style_business")
    builder.button(text="🚀 Технологии", callback_data="img_style_tech")
    builder.button(text="✨ Минимализм", callback_data="img_style_minimal")
    builder.button(text="🌈 Яркий",     callback_data="img_style_vibrant")
    builder.button(text="🌑 Тёмный",    callback_data="img_style_dark")
    builder.adjust(2)

    await state.update_data(img_type="og")
    await callback.message.answer("Выбери стиль:", reply_markup=builder.as_markup())
    await callback.answer()


# ─── Свободный промт ───
@router.callback_query(F.data == "img_type_free")
async def img_free_start(callback: CallbackQuery, state: FSMContext):
    await state.update_data(img_type="free", img_style="professional")
    await callback.message.answer("✏️ Опиши что нарисовать (на русском или английском):")
    await state.set_state(ImageStates.waiting_prompt)
    await callback.answer()


# ─── После выбора стиля — запрос темы ───
@router.callback_query(F.data.startswith("img_style_"))
async def img_style_chosen(callback: CallbackQuery, state: FSMContext):
    style = callback.data.replace("img_style_", "")
    await state.update_data(img_style=style)

    data = await state.get_data()
    img_type = data.get("img_type", "article")

    hint = "тему статьи" if img_type == "article" else "тему / заголовок"
    await callback.message.answer(f"📌 Введи {hint}:\n\nПример: _Как выбрать ноутбук для работы_", parse_mode="Markdown")
    await state.set_state(ImageStates.waiting_prompt)
    await callback.answer()


# ─── Генерация ───
@router.message(ImageStates.waiting_prompt)
async def img_generate(message: Message, state: FSMContext):
    data = await state.get_data()
    img_type = data.get("img_type", "free")
    img_style = data.get("img_style", "professional")

    await message.answer("⏳ Генерирую изображение через Pollinations.ai...")

    try:
        if img_type == "article":
            img_bytes = await generate_article_image(message.text, img_style)
        elif img_type == "og":
            img_bytes = await generate_og_image(message.text, img_style)
        else:
            img_bytes = await generate_image(message.text, img_style)

        if img_bytes:
            photo = BufferedInputFile(img_bytes, filename="image.jpg")

            builder = InlineKeyboardBuilder()
            builder.button(text="🔄 Ещё вариант", callback_data=f"img_regen")
            builder.button(text="🎨 Новое изображение", callback_data="img_new")
            builder.adjust(2)

            await state.update_data(last_prompt=message.text)
            await message.answer_photo(
                photo=photo,
                caption=f"✅ *Готово!*\nСтиль: {img_style}",
                parse_mode="Markdown",
                reply_markup=builder.as_markup()
            )
        else:
            await message.answer("❌ Не удалось сгенерировать. Попробуй другой промт.")

    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")

    await state.clear()


@router.callback_query(F.data == "img_regen")
async def img_regen(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    prompt = data.get("last_prompt", "abstract art")
    await callback.message.answer("⏳ Генерирую другой вариант...")
    img_bytes = await generate_image(prompt)
    if img_bytes:
        photo = BufferedInputFile(img_bytes, filename="image.jpg")
        await callback.message.answer_photo(photo=photo, caption="🔄 Новый вариант")
    await callback.answer()


@router.callback_query(F.data == "img_new")
async def img_new(callback: CallbackQuery, state: FSMContext):
    await image_menu(callback.message, state)
    await callback.answer()
