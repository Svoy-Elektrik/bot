import os

from aiogram import Bot

from utils import split_for_telegram


class TelegramChannelNotConfigured(Exception):
    """Raised when TG_CHANNEL_ID env var is missing."""


async def publish_to_telegram(bot: Bot, text: str) -> None:
    chat_id = os.getenv("TG_CHANNEL_ID")
    if not chat_id:
        raise TelegramChannelNotConfigured()
    try:
        target: int | str = int(chat_id)
    except ValueError:
        target = chat_id  # @channelusername
    for chunk in split_for_telegram(text):
        await bot.send_message(target, chunk)
