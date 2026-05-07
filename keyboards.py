from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def lang_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang:ru"),
        InlineKeyboardButton(text="🇩🇪 Deutsch", callback_data="lang:de"),
    ]])


def length_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="1000", callback_data="len:1000"),
            InlineKeyboardButton(text="2000", callback_data="len:2000"),
        ],
        [
            InlineKeyboardButton(text="3000", callback_data="len:3000"),
            InlineKeyboardButton(text="5000", callback_data="len:5000"),
        ],
    ])


def output_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📝 WordPress", callback_data="out:wp"),
            InlineKeyboardButton(text="📢 Telegram", callback_data="out:tg"),
        ],
        [InlineKeyboardButton(text="📋 Скопировать", callback_data="out:copy")],
        [InlineKeyboardButton(text="🔄 Новая статья", callback_data="restart")],
    ])
