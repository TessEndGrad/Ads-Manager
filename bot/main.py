import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import bot_settings
from bot.handlers import common, posts, moderation

logging.basicConfig(level=logging.INFO)

async def main():
    bot = Bot(token=bot_settings.BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(common.router)
    dp.include_router(posts.router)
    dp.include_router(moderation.router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())