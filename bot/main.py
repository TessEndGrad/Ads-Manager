import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import bot_settings
from bot.api_client import AdsAPIClient
from bot.scheduler import scheduler_loop
from bot.handlers import common, posts, moderation

logging.basicConfig(level=logging.INFO)

async def main():
    bot = Bot(token=bot_settings.BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(common.router)
    dp.include_router(posts.router)
    dp.include_router(moderation.router)

    client = AdsAPIClient(bot_settings.API_BASE_URL)
    bot_token = await client.login(
        bot_settings.BOT_API_EMAIL,
        bot_settings.BOT_API_PASSWORD
    )
    if not bot_token:
        raise RuntimeError("Не удалось авторизовать бота в API")

    # Запускаем планировщик параллельно с polling
    loop = asyncio.get_event_loop()
    loop.create_task(scheduler_loop(bot, bot_token))

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())