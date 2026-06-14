import asyncio
import logging
from datetime import datetime

import aiohttp
from aiogram import Bot
from aiogram.types import FSInputFile, InputMediaPhoto, InputMediaVideo

from bot.config import bot_settings

logger = logging.getLogger(__name__)


async def fetch_pending_publications(api_token: str) -> list[dict]:
    """Получаем все pending публикации у которых scheduled_at <= now"""
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{bot_settings.API_BASE_URL}/telegram/pending",
            headers={"Authorization": f"Bearer {api_token}"}
        ) as resp:
            if resp.status == 200:
                return await resp.json()
            return []


async def mark_published(api_token: str, pub_id: int, success: bool, error: str = None):
    async with aiohttp.ClientSession() as session:
        await session.patch(
            f"{bot_settings.API_BASE_URL}/telegram/publications/{pub_id}",
            headers={"Authorization": f"Bearer {api_token}"},
            json={"success": success, "error": error}
        )


async def publish_post(bot: Bot, publication: dict):
    post = publication["post"]
    chat_id = publication["chat_id"]

    title   = post.get("title") or ""
    content = post.get("content") or ""
    media   = post.get("media_items", [])

    caption = f"<b>{title}</b>\n\n{content}" if title else content

    try:
        if not media:
            # Только текст
            await bot.send_message(chat_id=chat_id, text=caption, parse_mode="HTML")

        elif len(media) == 1:
            item = media[0]
            file_url = f"{bot_settings.MEDIA_BASE_URL}{item['file_url']}"
            if item["media_type"] == "image":
                await bot.send_photo(chat_id=chat_id, photo=file_url, caption=caption, parse_mode="HTML")
            elif item["media_type"] == "video":
                await bot.send_video(chat_id=chat_id, video=file_url, caption=caption, parse_mode="HTML")

        else:
            # Медиагруппа
            media_group = []
            for i, item in enumerate(media[:10]):  # Telegram лимит — 10
                file_url = f"{bot_settings.MEDIA_BASE_URL}{item['file_url']}"
                cap = caption if i == 0 else None
                if item["media_type"] == "image":
                    media_group.append(InputMediaPhoto(media=file_url, caption=cap, parse_mode="HTML"))
                elif item["media_type"] == "video":
                    media_group.append(InputMediaVideo(media=file_url, caption=cap, parse_mode="HTML"))
            await bot.send_media_group(chat_id=chat_id, media=media_group)

        logger.info(f"✅ Пост {post['id']} опубликован в {chat_id}")
        return True, None

    except Exception as e:
        logger.error(f"❌ Ошибка публикации поста {post['id']}: {e}")
        return False, str(e)


async def scheduler_loop(bot: Bot, bot_api_token: str):
    """Запускается как фоновая задача, проверяет каждые 30 секунд"""
    logger.info("🕐 Планировщик запущен")
    while True:
        try:
            publications = await fetch_pending_publications(bot_api_token)
            for pub in publications:
                success, error = await publish_post(bot, pub)
                await mark_published(bot_api_token, pub["id"], success, error)
        except Exception as e:
            logger.error(f"Ошибка планировщика: {e}")
        await asyncio.sleep(30)