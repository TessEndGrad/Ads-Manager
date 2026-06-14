from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

def main_menu_user() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📋 Мои посты"), KeyboardButton(text="✏️ Создать пост")],
            [KeyboardButton(text="📝 Мои черновики"), KeyboardButton(text="👤 Профиль")],
            [KeyboardButton(text="🏷️ Теги")],
        ],
        resize_keyboard=True
    )

def main_menu_manager() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📋 Все посты"), KeyboardButton(text="✏️ Создать пост")],
            [KeyboardButton(text="🔍 На модерации"), KeyboardButton(text="👤 Профиль")],
            [KeyboardButton(text="🏷️ Теги")],
        ],
        resize_keyboard=True
    )

def post_actions(post_id: int, status_id: int, is_manager: bool) -> InlineKeyboardMarkup:
    buttons = []
    if status_id == 1 and not is_manager:  # draft, автор
        buttons.append([InlineKeyboardButton(
            text="📤 Отправить на модерацию",
            callback_data=f"submit_{post_id}"
        )])
    if status_id == 2 and is_manager:  # на модерации, менеджер
        buttons.append([
            InlineKeyboardButton(text="✅ Одобрить", callback_data=f"approve_{post_id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_{post_id}"),
        ])
    return InlineKeyboardMarkup(inline_keyboard=buttons) if buttons else None

def posts_pagination(page: int, total: int, page_size: int) -> InlineKeyboardMarkup:
    buttons = []
    row = []
    if page > 1:
        row.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"posts_page_{page-1}"))
    if page * page_size < total:
        row.append(InlineKeyboardButton(text="Вперёд ➡️", callback_data=f"posts_page_{page+1}"))
    if row:
        buttons.append(row)
    return InlineKeyboardMarkup(inline_keyboard=buttons) if buttons else None

def tags_menu(tags: list) -> InlineKeyboardMarkup:
    """Клавиатура со списком тегов"""
    buttons = []
    for tag in tags:
        buttons.append([InlineKeyboardButton(
            text=f"# {tag['name']} ({tag['posts_count']} постов)",
            callback_data=f"tag_{tag['id']}"
        )])
    buttons.append([InlineKeyboardButton(text="➕ Добавить тег", callback_data="add_tag")])
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def tag_selection(tags: list, selected_ids: list = None) -> InlineKeyboardMarkup:
    """Клавиатура для выбора тегов при создании поста"""
    if selected_ids is None:
        selected_ids = []
    
    buttons = []
    for tag in tags:
        is_selected = tag['id'] in selected_ids
        btn_text = f"✅ #{tag['name']}" if is_selected else f"⬜ #{tag['name']}"
        buttons.append([InlineKeyboardButton(
            text=btn_text,
            callback_data=f"select_tag_{tag['id']}"
        )])
    
    buttons.append([InlineKeyboardButton(text="➕ Создать новый тег", callback_data="create_new_tag")])
    buttons.append([InlineKeyboardButton(text="➡️ Далее (медиа)", callback_data="finish_tags")])
    buttons.append([InlineKeyboardButton(text="❌ Пропустить теги", callback_data="skip_tags")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def media_upload_menu() -> ReplyKeyboardMarkup:
    """Меню для загрузки медиа"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📷 Отправить фото")],
            [KeyboardButton(text="🎥 Отправить видео")],
            [KeyboardButton(text="⏭️ Пропустить")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def finish_post_creation() -> InlineKeyboardMarkup:
    """Завершить создание поста"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Создать пост", callback_data="create_post_final")],
        [InlineKeyboardButton(text="🔙 Назад к тегам", callback_data="back_to_tags")],
    ])