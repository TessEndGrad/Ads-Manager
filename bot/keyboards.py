from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

def main_menu_user() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📋 Мои посты"), KeyboardButton(text="✏️ Создать пост")],
            [KeyboardButton(text="📝 Мои черновики"), KeyboardButton(text="👤 Профиль")],
        ],
        resize_keyboard=True
    )

def main_menu_manager() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📋 Все посты"), KeyboardButton(text="✏️ Создать пост")],
            [KeyboardButton(text="🔍 На модерации"), KeyboardButton(text="👤 Профиль")],
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