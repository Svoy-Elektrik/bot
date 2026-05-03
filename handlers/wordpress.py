from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from services.wordpress_service import get_wp_sites, create_wp_post, upload_image_to_wp, markdown_to_html

router = Router()


class WPStates(StatesGroup):
    choosing_site = State()
    waiting_title = State()
    waiting_content = State()


@router.message(Command("wp"))
async def wp_menu(message: Message, state: FSMContext):
    sites = get_wp_sites()

    if not sites:
        await message.answer(
            "❌ Нет настроенных WP сайтов!\n\n"
            "Добавь в Railway Variables:\n"
            "`WP_SITE_1=https://yoursite.com|username|app_password`",
            parse_mode="Markdown"
        )
        return

    builder = InlineKeyboardBuilder()
    for i, site in enumerate(sites):
        builder.button(text=f"🌐 {site['url']}", callback_data=f"wp_site_{i}")
    builder.adjust(1)

    await state.update_data(sites=sites)
    await message.answer("🌐 Выбери сайт для публикации:", reply_markup=builder.as_markup())
    await state.set_state(WPStates.choosing_site)


@router.callback_query(F.data.startswith("wp_site_"))
async def wp_choose_site(callback: CallbackQuery, state: FSMContext):
    site_idx = int(callback.data.split("_")[-1])
    data = await state.get_data()
    sites = data.get("sites", get_wp_sites())

    await state.update_data(selected_site=sites[site_idx])
    await callback.message.answer("📝 Введи *заголовок поста*:", parse_mode="Markdown")
    await state.set_state(WPStates.waiting_title)
    await callback.answer()


@router.message(WPStates.waiting_title)
async def wp_get_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("📄 Отправь *текст статьи* (Markdown):", parse_mode="Markdown")
    await state.set_state(WPStates.waiting_content)


@router.message(WPStates.waiting_content)
async def wp_publish(message: Message, state: FSMContext):
    data = await state.get_data()
    site = data["selected_site"]
    title = data["title"]
    content_md = message.text

    await message.answer("⏳ Публикую на WordPress...")

    try:
        html_content = await markdown_to_html(content_md)
        result = await create_wp_post(
            site=site,
            title=title,
            content=html_content,
            status="draft"  # сначала черновик
        )

        if result:
            builder = InlineKeyboardBuilder()
            builder.button(text="✅ Опубликовать", callback_data=f"wp_publish_{result['id']}")
            await message.answer(
                f"✅ *Черновик создан!*\n\n"
                f"🔗 Просмотр: {result.get('link', 'N/A')}\n"
                f"ID: `{result['id']}`",
                parse_mode="Markdown",
                reply_markup=builder.as_markup()
            )
        else:
            await message.answer("❌ Ошибка публикации. Проверь данные WP сайта.")

    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")

    await state.clear()


# ─── Быстрая публикация из callback (после генерации статьи) ───
@router.callback_query(F.data == "publish_last")
async def publish_last_article(callback: CallbackQuery, state: FSMContext):
    sites = get_wp_sites()
    if not sites:
        await callback.message.answer("❌ Нет настроенных WP сайтов!")
        await callback.answer()
        return

    builder = InlineKeyboardBuilder()
    for i, site in enumerate(sites):
        builder.button(text=f"🌐 {site['url']}", callback_data=f"wp_quick_{i}")
    builder.adjust(1)

    await state.update_data(sites=sites)
    await callback.message.answer("🌐 На какой сайт публикуем?", reply_markup=builder.as_markup())
    await callback.answer()
