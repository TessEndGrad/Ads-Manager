from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.states import CreatePostStates
from bot.api_client import AdsAPIClient
from bot.keyboards import post_actions, posts_pagination
from bot.config import bot_settings
from bot.handlers.common import user_tokens, user_data

router = Router()
client = AdsAPIClient(bot_settings.API_BASE_URL)

STATUS_NAMES = {1: "📝 Черновик", 2: "🔍 На модерации", 3: "✅ Одобрен", 4: "🚀 Опубликован", 5: "❌ Отклонён"}


def format_post(post: dict) -> str:
    status = STATUS_NAMES.get(post.get("status_id", 0), "?")
    title = post.get("title") or "Без названия"
    content = (post.get("content") or "")[:200]
    return (
        f"📌 <b>{title}</b> [ID: {post['id']}]\n"
        f"Статус: {status}\n"
        f"📄 {content}{'...' if len(post.get('content') or '') > 200 else ''}"
    )


async def send_posts_page(message: Message, token: str, page: int, is_manager: bool):
    data = await client.get_posts(token, page=page, page_size=10)
    if not data or not data.get("items"):
        await message.answer("Постов не найдено.")
        return
    posts = data["items"]
    total = data["total"]
    text = f"📋 <b>Посты</b> (стр. {page}, всего {total})\n\n"
    text += "\n\n".join(format_post(p) for p in posts)
    kb = posts_pagination(page, total, 10)
    await message.answer(text, reply_markup=kb, parse_mode="HTML")


@router.message(F.text.in_(["📋 Мои посты", "📋 Все посты"]))
async def list_posts(message: Message):
    tg_id = message.from_user.id
    token = user_tokens.get(tg_id)
    if not token:
        await message.answer("Вы не авторизованы. Введите /start")
        return
    me = user_data.get(tg_id, {})
    await send_posts_page(message, token, page=1, is_manager=me.get("role_id") == 1)


@router.callback_query(F.data.startswith("posts_page_"))
async def paginate_posts(callback: CallbackQuery):
    tg_id = callback.from_user.id
    token = user_tokens.get(tg_id)
    if not token:
        await callback.answer("Не авторизован")
        return
    page = int(callback.data.split("_")[-1])
    me = user_data.get(tg_id, {})
    await send_posts_page(callback.message, token, page, is_manager=me.get("role_id") == 1)
    await callback.answer()


@router.message(F.text == "📝 Мои черновики")
async def my_drafts(message: Message):
    tg_id = message.from_user.id
    token = user_tokens.get(tg_id)
    if not token:
        await message.answer("Вы не авторизованы. Введите /start")
        return
    data = await client.get_posts(token, page=1, page_size=20)
    if not data:
        await message.answer("Ошибка получения постов")
        return
    drafts = [p for p in data.get("items", []) if p.get("status_id") == 1]
    if not drafts:
        await message.answer("У вас нет черновиков.")
        return
    text = "📝 <b>Мои черновики:</b>\n\n"
    for p in drafts:
        kb = post_actions(p["id"], p["status_id"], is_manager=False)
        await message.answer(format_post(p), reply_markup=kb, parse_mode="HTML")


@router.message(F.text == "✏️ Создать пост")
async def start_create_post(message: Message, state: FSMContext):
    tg_id = message.from_user.id
    if tg_id not in user_tokens:
        await message.answer("Вы не авторизованы. Введите /start")
        return
    await message.answer("📝 Введите <b>заголовок</b> поста:", parse_mode="HTML")
    await state.set_state(CreatePostStates.waiting_title)


@router.message(CreatePostStates.waiting_title)
async def create_post_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text.strip())
    await message.answer("📄 Теперь введите <b>текст</b> поста:", parse_mode="HTML")
    await state.set_state(CreatePostStates.waiting_content)


@router.message(CreatePostStates.waiting_content)
async def create_post_content(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    tg_id = message.from_user.id
    token = user_tokens[tg_id]
    post = await client.create_post(token, title=data["title"], content=message.text.strip())
    if not post:
        await message.answer("❌ Ошибка при создании поста")
        return
    kb = post_actions(post["id"], post["status_id"], is_manager=False)
    await message.answer(
        f"✅ Пост создан!\n\n{format_post(post)}",
        reply_markup=kb, parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("submit_"))
async def submit_post(callback: CallbackQuery):
    tg_id = callback.from_user.id
    token = user_tokens.get(tg_id)
    post_id = int(callback.data.split("_")[1])
    result = await client.submit_post(token, post_id)
    if result:
        await callback.message.edit_text(
            f"📤 Пост отправлен на модерацию!\n\n{format_post(result)}",
            parse_mode="HTML"
        )
    else:
        await callback.answer("❌ Не удалось отправить на модерацию")
    await callback.answer()