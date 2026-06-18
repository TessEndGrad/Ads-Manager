from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import ChatMemberUpdated
from aiogram.filters import ChatMemberUpdatedFilter
from aiogram.enums import ChatMemberStatus

from bot.states import AuthStates
from bot.api_client import AdsAPIClient
from bot.keyboards import main_menu_user, main_menu_manager
from bot.config import bot_settings

router = Router()
client = AdsAPIClient(bot_settings.API_BASE_URL)

# Хранилище токенов в памяти: {telegram_user_id: token}
# В продакшене замените на Redis или БД
user_tokens: dict[int, str] = {}
user_data: dict[int, dict] = {}


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    tg_id = message.from_user.id
    if tg_id in user_tokens:
        me = await client.get_me(user_tokens[tg_id])
        if me:
            is_manager = me.get("role_id") == 1
            kb = main_menu_manager() if is_manager else main_menu_user()
            await message.answer(
                f"👋 С возвращением, <b>{me['username']}</b>!", 
                reply_markup=kb, parse_mode="HTML"
            )
            return

    await message.answer(
        "👋 Добро пожаловать в <b>Ads Manager</b>!\n\n"
        "Введите ваш <b>email</b> для входа:",
        parse_mode="HTML"
    )
    await state.set_state(AuthStates.waiting_email)


@router.message(AuthStates.waiting_email)
async def process_email(message: Message, state: FSMContext):
    await state.update_data(email=message.text.strip())
    await message.answer("🔐 Теперь введите <b>пароль</b>:", parse_mode="HTML")
    await state.set_state(AuthStates.waiting_password)


@router.message(AuthStates.waiting_password)
async def process_password(message: Message, state: FSMContext):
    data = await state.get_data()
    email = data["email"]
    password = message.text.strip()
    await state.clear()

    token = await client.login(email, password)
    if not token:
        await message.answer("❌ Неверный email или пароль. Попробуйте ещё раз /start")
        return

    tg_id = message.from_user.id
    user_tokens[tg_id] = token

    me = await client.get_me(token)
    user_data[tg_id] = me
    is_manager = me.get("role_id") == 1
    kb = main_menu_manager() if is_manager else main_menu_user()

    await message.answer(
        f"✅ Вы вошли как <b>{me['username']}</b> "
        f"({'Менеджер' if is_manager else 'Пользователь'})",
        reply_markup=kb, parse_mode="HTML"
    )


@router.message(F.text == "👤 Профиль")
async def profile(message: Message):
    tg_id = message.from_user.id
    token = user_tokens.get(tg_id)
    if not token:
        await message.answer("Вы не авторизованы. Введите /start")
        return
    me = await client.get_me(token)
    if not me:
        await message.answer("Не удалось получить профиль")
        return
    await message.answer(
        f"👤 <b>Профиль</b>\n\n"
        f"Имя: {me['username']}\n"
        f"Email: {me['email']}\n"
        f"Роль: {'Менеджер' if me['role_id'] == 1 else 'Пользователь'}",
        parse_mode="HTML"
    )




# Обработка добавления бота в чат
@router.my_chat_member(ChatMemberUpdatedFilter(
    member_status_changed=(ChatMemberStatus.LEFT, ChatMemberStatus.MEMBER)
))
async def bot_added_to_chat(event: ChatMemberUpdated):
    chat_id = event.chat.id
    chat_title = event.chat.title
    chat_type = event.chat.type
    
    # Отправляем информацию на API для сохранения
    await client.add_telegram_chat(
        chat_id=str(chat_id),
        title=chat_title,
        chat_type=chat_type
    )
    
    await event.bot.send_message(
        chat_id=chat_id,
        text="✅ Бот успешно добавлен! Теперь вы можете публиковать посты в этот чат через Ads Manager."
    )