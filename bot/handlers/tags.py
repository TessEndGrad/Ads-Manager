from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from bot.api_client import AdsAPIClient
from bot.config import bot_settings
from bot.handlers.common import user_tokens
from bot.keyboards import tags_menu
from bot.states import AddTagStates

router = Router()
client = AdsAPIClient(bot_settings.API_BASE_URL)

@router.message(F.text == "🏷️ Теги")
async def show_tags(message: Message):
    tg_id = message.from_user.id
    token = user_tokens.get(tg_id)
    if not token:
        await message.answer("Вы не авторизованы. Введите /start")
        return
    
    tags = await client.get_tags(token, limit=50)
    if not tags:
        await message.answer("🏷️ У вас пока нет тегов.\n\n"
                           "Используйте кнопку 'Добавить тег' чтобы создать первый.")
        return
    
    text = "🏷️ <b>Ваши теги:</b>\n\n"
    for tag in tags:
        text += f"# {tag['name']} — {tag['posts_count']} пост(ов)\n"
    
    await message.answer(text, reply_markup=tags_menu(tags), parse_mode="HTML")

@router.callback_query(F.data == "add_tag")
async def start_add_tag(callback: CallbackQuery, state):
    await callback.message.answer("🏷️ Введите название нового тега:")
    await state.set_state(AddTagStates.waiting_tag_name)
    await callback.answer()

@router.message(AddTagStates.waiting_tag_name)
async def process_add_tag(message: Message, state):
    tag_name = message.text.strip().lower()
    tg_id = message.from_user.id
    token = user_tokens.get(tg_id)
    
    if not token:
        await message.answer("Ошибка авторизации")
        await state.clear()
        return
    
    new_tag = await client.create_tag(token, tag_name)
    if new_tag:
        await message.answer(f"✅ Тег '#{tag_name}' создан!")
        await show_tags(message)
    else:
        await message.answer("❌ Не удалось создать тег. Возможно, он уже существует.")
    
    await state.clear()

@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery):
    from bot.keyboards import main_menu_user, main_menu_manager
    from bot.handlers.common import user_data
    
    tg_id = callback.from_user.id
    me = user_data.get(tg_id, {})
    is_manager = me.get("role_id") == 1
    
    kb = main_menu_manager() if is_manager else main_menu_user()
    await callback.message.answer(" Главное меню:", reply_markup=kb)
    await callback.answer()