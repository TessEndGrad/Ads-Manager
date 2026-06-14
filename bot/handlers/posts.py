from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from bot.states import CreatePostStates
from bot.api_client import AdsAPIClient
from bot.keyboards import post_actions, posts_pagination, tag_selection, media_upload_menu, finish_post_creation
from bot.config import bot_settings
from bot.handlers.common import user_tokens, user_data
import os
import tempfile

router = Router()
client = AdsAPIClient(bot_settings.API_BASE_URL)

STATUS_NAMES = {1: "📝 Черновик", 2: "🔍 На модерации", 3: "✅ Одобрен", 4: "🚀 Опубликован", 5: "❌ Отклонён"}

def format_post(post: dict) -> str:
    status = STATUS_NAMES.get(post.get("status_id", 0), "?")
    title = post.get("title") or "Без названия"
    content = (post.get("content") or "")[:200]
    tags = ", ".join([f"#{t['name']}" for t in post.get("tags", [])])
    
    return (
        f"📌 <b>{title}</b> [ID: {post['id']}]\n"
        f"Статус: {status}\n"
        f"📄 {content}{'...' if len(post.get('content') or '') > 200 else ''}\n"
        f"🏷️ Теги: {tags if tags else 'нет'}"
    )

async def send_posts_page(message: Message, token: str, page: int, is_manager: bool):
    data = await client.get_posts(token, page=page, page_size=10)
    if not data or not data.get("items"):
        await message.answer("Постов не найдено.")
        return
    posts = data["items"]
    total = data["total"]
    text = f"📋 <b>Посты</b> (стр. {page}, всего {total})\n\n"
    text += "\n".join(format_post(p) for p in posts)
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
    
    await state.update_data(title=None, content=None, tag_ids=[], media_files=[])
    await message.answer("📝 Введите <b>заголовок</b> поста:", parse_mode="HTML")
    await state.set_state(CreatePostStates.waiting_title)

@router.message(CreatePostStates.waiting_title)
async def create_post_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text.strip())
    await message.answer("📄 Теперь введите <b>текст</b> поста:", parse_mode="HTML")
    await state.set_state(CreatePostStates.waiting_content)

@router.message(CreatePostStates.waiting_content)
async def create_post_content(message: Message, state: FSMContext):
    await state.update_data(content=message.text.strip())
    
    # Загружаем теги
    tg_id = message.from_user.id
    token = user_tokens[tg_id]
    tags = await client.get_tags(token, limit=50)
    
    if tags:
        await message.answer(
            "🏷️ <b>Выберите теги</b> (можно несколько):\n\n"
            "Нажимайте на теги для выбора/снятия выделения.\n"
            "Когда закончите — нажмите 'Далее'",
            reply_markup=tag_selection(tags, []),
            parse_mode="HTML"
        )
    else:
        await message.answer("🏷️ У вас пока нет тегов. Переходим к загрузке медиа...")
        await state.set_state(CreatePostStates.waiting_media)
        await message.answer(
            "📎 <b>Загрузите фото или видео</b> (или пропустите):",
            reply_markup=media_upload_menu(),
            parse_mode="HTML"
        )

@router.callback_query(F.data.startswith("select_tag_"))
async def toggle_tag_selection(callback: CallbackQuery, state: FSMContext):
    tag_id = int(callback.data.split("_")[-1])
    data = await state.get_data()
    selected_ids = data.get("tag_ids", [])
    
    if tag_id in selected_ids:
        selected_ids.remove(tag_id)
    else:
        selected_ids.append(tag_id)
    
    await state.update_data(tag_ids=selected_ids)
    
    # Обновляем клавиатуру
    tg_id = callback.from_user.id
    token = user_tokens[tg_id]
    tags = await client.get_tags(token, limit=50)
    
    await callback.message.edit_text(
        "🏷️ <b>Выберите теги</b> (можно несколько):\n\n"
        "Нажимайте на теги для выбора/снятия выделения.\n"
        "Когда закончите — нажмите 'Далее'",
        reply_markup=tag_selection(tags, selected_ids),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "skip_tags")
async def skip_tags(callback: CallbackQuery, state: FSMContext):
    await state.set_state(CreatePostStates.waiting_media)
    await callback.message.answer(
        "📎 <b>Загрузите фото или видео</b> (или пропустите):",
        reply_markup=media_upload_menu(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "finish_tags")
async def finish_tags_selection(callback: CallbackQuery, state: FSMContext):
    await state.set_state(CreatePostStates.waiting_media)
    await callback.message.answer(
        "📎 <b>Загрузите фото или видео</b> (или пропустите):",
        reply_markup=media_upload_menu(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "create_new_tag")
async def create_new_tag(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("🏷️ Введите название нового тега:")
    await state.set_state(CreatePostStates.waiting_tags)

@router.message(CreatePostStates.waiting_tags)
async def process_new_tag(message: Message, state: FSMContext):
    tag_name = message.text.strip()
    tg_id = message.from_user.id
    token = user_tokens[tg_id]
    
    # Создаем тег
    new_tag = await client.create_tag(token, tag_name)
    
    if new_tag:
        await message.answer(f"✅ Тег '#{tag_name}' создан!")
        
        # Загружаем обновленный список тегов
        tags = await client.get_tags(token, limit=50)
        
        await message.answer(
            "🏷️ <b>Выберите теги</b> (можно несколько):",
            reply_markup=tag_selection(tags, []),
            parse_mode="HTML"
        )
        await state.set_state(CreatePostStates.waiting_content)  # Возвращаемся к предыдущему шагу
    else:
        await message.answer("❌ Не удалось создать тег. Попробуйте снова:")

@router.message(F.text == "📷 Отправить фото")
async def wait_photo(message: Message, state: FSMContext):
    await message.answer("📷 Отправьте фото:")
    await state.set_state(CreatePostStates.waiting_media)

@router.message(F.text == "🎥 Отправить видео")
async def wait_video(message: Message, state: FSMContext):
    await message.answer("🎥 Отправьте видео:")
    await state.set_state(CreatePostStates.waiting_media)

@router.message(CreatePostStates.waiting_media, F.photo)
async def handle_photo(message: Message, state: FSMContext):
    # Скачиваем фото
    photo = message.photo[-1]  # Берем наибольшее качество
    file = await message.bot.get_file(photo.file_id)
    
    # Создаем временный файл
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
    await message.bot.download_file(file.file_path, temp_file.name)
    
    # Сохраняем путь
    data = await state.get_data()
    media_files = data.get("media_files", [])
    media_files.append({"path": temp_file.name, "type": "photo"})
    await state.update_data(media_files=media_files)
    
    await message.answer("✅ Фото добавлено! Отправьте ещё или нажмите 'Готово':",
                        reply_markup=finish_post_creation())

@router.message(CreatePostStates.waiting_media, F.video)
async def handle_video(message: Message, state: FSMContext):
    video = message.video
    file = await message.bot.get_file(video.file_id)
    
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    await message.bot.download_file(file.file_path, temp_file.name)
    
    data = await state.get_data()
    media_files = data.get("media_files", [])
    media_files.append({"path": temp_file.name, "type": "video"})
    await state.update_data(media_files=media_files)
    
    await message.answer("✅ Видео добавлено! Отправьте ещё или нажмите 'Готово':",
                        reply_markup=finish_post_creation())

@router.callback_query(F.data == "create_post_final")
async def finalize_post_creation(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    title = data.get("title")
    content = data.get("content")
    tag_ids = data.get("tag_ids", [])
    media_files = data.get("media_files", [])
    
    tg_id = callback.from_user.id
    token = user_tokens[tg_id]
    
    # Создаем пост
    post = await client.create_post(token, title, content, tag_ids)
    
    if not post:
        await callback.message.answer("❌ Ошибка при создании поста")
        await state.clear()
        await callback.answer()
        return
    
    # Загружаем медиафайлы
    for media in media_files:
        await client.upload_media(token, post["id"], media["path"])
        # Удаляем временный файл
        try:
            os.unlink(media["path"])
        except:
            pass
    
    await callback.message.answer(
        f"✅ <b>Пост создан!</b>\n\n{format_post(post)}",
        parse_mode="HTML"
    )
    await state.clear()
    await callback.answer()

@router.callback_query(F.data == "back_to_tags")
async def back_to_tags(callback: CallbackQuery, state: FSMContext):
    tg_id = callback.from_user.id
    token = user_tokens[tg_id]
    tags = await client.get_tags(token, limit=50)
    data = await state.get_data()
    selected_ids = data.get("tag_ids", [])
    
    await callback.message.answer(
        "🏷️ <b>Выберите теги</b>:",
        reply_markup=tag_selection(tags, selected_ids),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("submit_"))
async def submit_post(callback: CallbackQuery):
    tg_id = callback.from_user.id
    token = user_tokens.get(tg_id)
    post_id = int(callback.data.split("_")[1])
    result = await client.submit_post(token, post_id)
    if result:
        await callback.message.edit_text(
            f"📤 Пост отправлен на модерацию!\n{format_post(result)}",
            parse_mode="HTML"
        )
    else:
        await callback.answer("❌ Не удалось отправить на модерацию")
    await callback.answer()