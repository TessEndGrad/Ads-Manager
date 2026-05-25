from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class TagOut(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class MediaOut(BaseModel):
    id: int
    file_url: str
    media_type: str
    created_at: Optional[datetime]

    model_config = {"from_attributes": True}


class PostOut(BaseModel):
    id: int
    title: Optional[str]
    content: Optional[str]
    author_id: int
    post_type_id: Optional[int]
    status_id: int
    scheduled_at: Optional[datetime]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    tags: list[TagOut] = []
    media: list[MediaOut] = []

    model_config = {"from_attributes": True}


class PostListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[PostOut]