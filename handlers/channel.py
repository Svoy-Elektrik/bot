import os
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from services.claude_service import generate_channel_post
from services.image_service import generate_image

router = Router()

CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")  # например: @mychannel или -1001234567890


class ChannelStates(StatesGroup):
    waiting_topic = State()
    waiting_custom_post = State()


@router.message(Command("channel"))
async def channel_menu(message: Message):
    if not CHANNEL_ID:
        await message.answer(
            "❌ Канал не настроен!\n\n"
            "Добавь в Railway Variables:\n"
            "`TELEGRAM_CHANNEL_ID=@yourchannelname`",
            parse_mode="Markdown"
        )
        return

    builder = InlineKeyboardBuilder()
    builder.button(text="🤖 Авто-пост по теме", callback_data="ch_auto")
    builder.button(text="✏️ Свой текст", callback_data="ch_custom")
    builder.button(text="📢 Переслать статью", callback_data="ch_forward")
    builder.adjust(1)

    await message.answer(
        f"📢 *Постинг в канал*\n\nКанал: `{CHANNEL_ID}`",
        parse_mode="Markdown",
        reply_markup=builder.as_markup()
    )


@router.callback_query(F.data == "ch_auto")
async def channel_auto_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("📌 Введи *тему поста* для канала:", parse_mode="Markdown")
    await state.set_state(ChannelStates.waiting_topic)
    await callback.answer()


@router.message(ChannelStates.waiting_topic)
async def channel_auto_post(message: Message, state: FSMContext, bot: Bot):
    topic = message.text
    await message.answer("⏳ Генерирую пост и изображение...")

    try:
        # Генерируем текст поста
        post_text = await generate_channel_post(topic)

        # Генерируем изображение
        img_bytes = await generate_image(topic, "social media post, vibrant, eye-catching")

        # Показываем превью
        builder = InlineKeyboardBuilder()
        builder.button(text="✅ Опубликовать", callback_data="ch_confirm")
        builder.button(text="🔄 Перегенерировать", callback_data="ch_auto")
        builder.button(text="❌ Отмена", callback_data="ch_cancel")
        builder.adjust(2, 1)

        await state.update_data(post_text=post_text, img_bytes=img_bytes, topic=topic)

        if img_bytes:
            photo = BufferedInputFile(img_bytes, filename="post.jpg")
            await message.answer_photo(
                photo=photo,
                caption=f"👁 *Превью поста:*\n\n{post_text}",
                parse_mode="Markdown",
                reply_markup=builder.as_markup()
            )
        else:
            await message.answer(
                f"👁 *Превью поста:*\n\n{post_text}",
                parse_mode="Markdown",
                reply_markup=builder.as_markup()
            )

    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")

    await state.clear()


@router.callback_query(F.data == "ch_confirm")
async def channel_publish(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    post_text = data.get("post_text", "")
    img_bytes = data.get("img_bytes")

    try:
        if img_bytes:
            photo = BufferedInputFile(img_bytes, filename="post.jpg")
            await bot.send_photo(
                chat_id=CHANNEL_ID,
                photo=photo,
                caption=post_text,
                parse_mode="Markdown"
            )
        else:
            await bot.send_message(
                chat_id=CHANNEL_ID,
                text=post_text,
                parse_mode="Markdown"
            )

        await callback.message.answer("✅ Пост опубликован в канале!")
    except Exception as e:
        await callback.message.answer(f"❌ Ошибка публикации: {e}")

    await callback.answer()


@router.callback_query(F.data == "ch_custom")
async def channel_custom_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("✏️ Введи текст поста (поддерживается Telegram Markdown):")
    await state.set_state(ChannelStates.waiting_custom_post)
    await callback.answer()


@router.message(ChannelStates.waiting_custom_post)
async def channel_custom_post(message: Message, state: FSMContext, bot: Bot):
    try:
        await bot.send_message(
            chat_id=CHANNEL_ID,
            text=message.text,
            parse_mode="Markdown"
        )
        await message.answer("✅ Пост опубликован!")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")
    await state.clear()


@router.callback_query(F.data == "post_to_channel")
async def post_article_to_channel(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    topic = data.get("last_topic", "")
    article = data.get("last_article", "")

    if not article:
        await callback.message.answer("❌ Нет статьи для публикации.")
        await callback.answer()
        return

    post_text = await generate_channel_post(topic, "")

    try:
        await bot.send_message(chat_id=CHANNEL_ID, text=post_text, parse_mode="Markdown")
        await callback.message.answer("✅ Анонс статьи опубликован в канале!")
    except Exception as e:
        await callback.message.answer(f"❌ Ошибка: {e}")

    await callback.answer()
