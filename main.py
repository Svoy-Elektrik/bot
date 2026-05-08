import asyncio
import logging
import os

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from handlers.start import router as start_router
from handlers.generate import router as gen_router
from handlers.output import router as output_router
from handlers.voice import router as voice_router

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
log = logging.getLogger(__name__)


async def main() -> None:
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("BOT_TOKEN is not set")
    if not os.getenv("CLAUDE_API_KEY"):
        raise RuntimeError("CLAUDE_API_KEY is not set")

    bot = Bot(token=token)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(start_router)
    dp.include_router(gen_router)
    dp.include_router(output_router)
    dp.include_router(voice_router)

    tg_channel = os.getenv("TG_CHANNEL_ID")
    wp_url = os.getenv("WP_URL")
    log.info(
        "Bot starting… TG_CHANNEL_ID=%s  WP_URL=%s",
        repr(tg_channel) if tg_channel else "NOT SET",
        repr(wp_url) if wp_url else "NOT SET",
    )
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
