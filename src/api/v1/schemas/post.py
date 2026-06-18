from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_validator, ConfigDict


class TagOut(BaseModel):
    id:   int
    name: str
    model_config = {"from_attributes": True}


class MediaOut(BaseModel):
    id:         int
    file_url:   str
    media_type: str
    created_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class StatusOut(BaseModel):
    id:   int
    name: str
    model_config = {"from_attributes": True}


class PostOut(BaseModel):
    id:           int
    title:        Optional[str]      = None
    content:      Optional[str]      = None
    author_id:    int
    post_type_id: Optional[int]      = None
    status_id:    int
    status:       Optional[StatusOut]= None
    scheduled_at: Optional[datetime] = None

    @field_validator("scheduled_at", mode="before")
    @classmethod
    def parse_scheduled_at(cls, v):
        if v is None:
            return v
        if isinstance(v, datetime):
            # Если datetime без timezone, считаем что это UTC
            if v.tzinfo is None:
                from datetime import timezone
                v = v.replace(tzinfo=timezone.utc)
            return v
        return v

    created_at:   Optional[datetime] = None
    updated_at:   Optional[datetime] = None
    tags:         list[TagOut]        = []
    media_items:  list[MediaOut]      = []
    model_config = {"from_attributes": True}


class PostListResponse(BaseModel):
    total:     int
    page:      int
    page_size: int
    items:     list[PostOut]


class PostCreate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    post_type_id: Optional[int] = None
    tag_ids: list[int] = []
    scheduled_at: Optional[datetime] = None

    @field_validator("scheduled_at", mode="after")
    @classmethod
    def strip_timezone(cls, v):
        if isinstance(v, datetime) and v.tzinfo is not None:
            return v.replace(tzinfo=None)
        return v


class PostUpdate(BaseModel):
    title:        Optional[str]      = None
    content:      Optional[str]      = None
    post_type_id: Optional[int]      = None
    scheduled_at: Optional[datetime] = None
    tag_ids:      Optional[list[int]]= None


class ScheduleRequest(BaseModel):
    scheduled_at: datetime

class TelegramScheduleRequest(BaseModel):
    chat_id: str         # например "-1001234567890"
    scheduled_at: datetime

class TelegramPublicationOut(BaseModel):
    id: int
    post_id: int
    chat_id: str
    scheduled_at: datetime
    published_at: Optional[datetime] = None
    status: str

    model_config = ConfigDict(from_attributes=True)