from aiogram.fsm.state import State, StatesGroup

class AuthStates(StatesGroup):
    waiting_email    = State()
    waiting_password = State()

class CreatePostStates(StatesGroup):
    waiting_title   = State()
    waiting_content = State()
    waiting_tags    = State()
    waiting_media   = State()

class RejectStates(StatesGroup):
    waiting_post_id = State()

class AddTagStates(StatesGroup):
    waiting_tag_name = State()