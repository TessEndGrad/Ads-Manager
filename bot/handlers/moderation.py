from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from bot.api_client import AdsAPIClient
from bot.keyboards import post_actions
from bot.config import bot_settings
from bot.handlers.common import user_tokens, user_data
from bot.handlers.posts import format_post

router = Router()
client = AdsAPIClient(bot_settings.API_BASE_URL)


@router.message(F.text == "🔍 На модерации")
async def posts_on_moderation(message: Message):
    tg_id = message.from_user.id
    token = user_tokens.get(tg_id)
    me = user_data.get(tg_id, {})
    if not token or me.get("role_id") != 1:
        await message.answer("❌ Доступ только для менеджеров")
        return
    data = await client.get_posts_on_moderation(token)
    if not data or not data.get("items"):
        await message.answer("🎉 Постов на модерации нет!")
        return
    posts = data["items"]
    await message.answer(f"🔍 <b>На модерации: {len(posts)} постов</b>", parse_mode="HTML")
    for p in posts:
        kb = post_actions(p["id"], p["status_id"], is_manager=True)
        await message.answer(format_post(p), reply_markup=kb, parse_mode="HTML")


@router.callback_query(F.data.startswith("approve_"))
async def approve_post(callback: CallbackQuery):
    tg_id = callback.from_user.id
    token = user_tokens.get(tg_id)
    me = user_data.get(tg_id, {})
    if not token or me.get("role_id") != 1:
        await callback.answer("❌ Нет прав")
        return
    post_id = int(callback.data.split("_")[1])
    result = await client.approve_post(token, post_id)
    if result:
        await callback.message.edit_text(
            f"✅ Пост одобрен!\n\n{format_post(result)}", parse_mode="HTML"
        )
    else:
        await callback.answer("❌ Ошибка при одобрении")
    await callback.answer()


@router.callback_query(F.data.startswith("reject_"))
async def reject_post(callback: CallbackQuery):
    tg_id = callback.from_user.id
    token = user_tokens.get(tg_id)
    me = user_data.get(tg_id, {})
    if not token or me.get("role_id") != 1:
        await callback.answer("❌ Нет прав")
        return
    post_id = int(callback.data.split("_")[1])
    result = await client.reject_post(token, post_id)
    if result:
        await callback.message.edit_text(
            f"❌ Пост отклонён!\n\n{format_post(result)}", parse_mode="HTML"
        )
    else:
        await callback.answer("❌ Ошибка при отклонении")
    await callback.answer()