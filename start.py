from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

router = Router()

HELP_TEXT = """
🤖 *SEO Bot — Твой контент-помощник*

Команды:

✍️ /seo — SEO статьи и рерайт
  • Генерация уникальных SEO статей
  • Рерайт и уникализация текста
  • Генерация мета-тегов

🎨 /image — Генерация изображений
  • Создание картинок для статей
  • Через Ideogram или DALL-E

🔍 /check — Проверка на плагиат
  • Проверка уникальности через Text.ru
  • Детальный отчёт

🌐 /wp — Публикация в WordPress
  • Поддержка нескольких сайтов
  • Авто-конвертация Markdown → HTML
  • Загрузка изображений в медиатеку

📢 /channel — Ведение Telegram канала
  • Авто-генерация постов
  • Публикация с изображением
  • Анонс статей

📋 /help — Эта справка
"""


@router.message(Command("start"))
async def start(message: Message):
    await message.answer(
        f"Привет, {message.from_user.first_name}! 👋\n" + HELP_TEXT,
        parse_mode="Markdown"
    )


@router.message(Command("help"))
async def help_cmd(message: Message):
    await message.answer(HELP_TEXT, parse_mode="Markdown")
