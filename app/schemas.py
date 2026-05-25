from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import List, Optional

# --- Схемы для Тегов ---
class TagBase(BaseModel):
    name: str

class TagResponse(TagBase):
    id: int
    
    # Позволяет Pydantic автоматически читать данные из ORM-моделей SQLAlchemy
    model_config = ConfigDict(from_attributes=True)


class PopularTagResponse(TagResponse):
    posts_count: int  # Дополнительное поле для топа тегов


# --- Схемы для Медиа ---
class MediaResponse(BaseModel):
    id: int
    file_url: str
    media_type: str
    
    model_config = ConfigDict(from_attributes=True)


# --- Схемы для Постов ---
class PostResponse(BaseModel):
    id: int
    title: Optional[str] = None
    content: Optional[str] = None
    author_id: int
    status_id: int
    scheduled_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    tags: List[TagResponse] = []  # Список вложенных тегов
    media: List[MediaResponse] = []  # Список вложенных медиафайлов

    model_config = ConfigDict(from_attributes=True)


# --- Схемы для Интеграций ---
class IntegrationStatusResponse(BaseModel):
    account_name: Optional[str]
    platform: str
    is_active: bool
    expires_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)