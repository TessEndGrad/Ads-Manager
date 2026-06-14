import os
import uuid
from fastapi import UploadFile, File, HTTPException

from datetime import datetime
from typing import Optional, Literal

from fastapi import APIRouter, Depends, Query

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.dependencies import get_db, get_current_user
from src.api.v1.dependencies import get_post_service
from src.api.v1.schemas.post import PostOut, PostListResponse, PostCreate, PostUpdate, ScheduleRequest
from src.infrastructure.persistence.models.models import Post
from src.core.dependencies import get_current_user
from src.infrastructure.persistence.repositories.post_repository import PostFilters
from src.modules.posts.service import PostService
from src.api.v1.schemas.post import TelegramScheduleRequest, TelegramPublicationOut
from src.infrastructure.persistence.models.models import TelegramPublication

router = APIRouter(prefix="/posts", tags=["Посты"])


@router.get("/", response_model=PostListResponse, summary="Список постов")
async def get_posts(
    page:           int = Query(1, ge=1),
    page_size:      int = Query(20, ge=1, le=100),
    status_id:      Optional[int]  = Query(None),
    post_type_id:   Optional[int]  = Query(None),
    author_id:      Optional[int]  = Query(None),
    tag_ids:        Optional[list[int]] = Query(None),
    scheduled_from: Optional[datetime] = Query(None),
    scheduled_to:   Optional[datetime] = Query(None),
    created_from:   Optional[datetime] = Query(None),
    created_to:     Optional[datetime] = Query(None),
    search:         Optional[str]  = Query(None),
    order_by:  Literal["created_at","updated_at","scheduled_at","title","status_id"] = Query("created_at"),
    order_dir: Literal["asc","desc"] = Query("desc"),
    service: PostService = Depends(get_post_service),
    current_user = Depends(get_current_user),
):
    filters = PostFilters(
        status_id=status_id, post_type_id=post_type_id, author_id=author_id,
        tag_ids=tag_ids or [], scheduled_from=scheduled_from, scheduled_to=scheduled_to,
        created_from=created_from, created_to=created_to, search=search,
    )
    posts, total = await service.get_posts(filters, order_by, order_dir, page, page_size, current_user)
    return PostListResponse(total=total, page=page, page_size=page_size, items=posts)


@router.get("/my-drafts", response_model=list[PostOut], summary="Мои черновики")
async def get_my_drafts(
    service: PostService = Depends(get_post_service),
    current_user = Depends(get_current_user),
):
    return await service.get_my_drafts(current_user)


@router.get("/{post_id}", response_model=PostOut, summary="Получить пост по ID")
async def get_post(
    post_id: int,
    service: PostService = Depends(get_post_service),
    current_user = Depends(get_current_user),
):
    return await service.get_by_id(post_id, current_user)


@router.post("/", response_model=PostOut, status_code=201, summary="Создать пост")
async def create_post(
    data: PostCreate,
    service: PostService = Depends(get_post_service),
    current_user = Depends(get_current_user),
):
    return await service.create_post(data, current_user)


@router.put("/{post_id}", response_model=PostOut, summary="Обновить пост")
async def update_post(
    post_id: int,
    data: PostUpdate,
    service: PostService = Depends(get_post_service),
    current_user = Depends(get_current_user),
):
    return await service.update_post(post_id, data, current_user)


@router.delete("/{post_id}", status_code=204, summary="Удалить пост")
async def delete_post(
    post_id: int,
    service: PostService = Depends(get_post_service),
    current_user = Depends(get_current_user),
):
    await service.delete_post(post_id, current_user)


@router.post("/{post_id}/submit", response_model=PostOut, summary="Отправить на модерацию")
async def submit_post(
    post_id: int,
    service: PostService = Depends(get_post_service),
    current_user = Depends(get_current_user),
):
    return await service.submit_post(post_id, current_user)


@router.post("/{post_id}/approve", response_model=PostOut, summary="Одобрить пост")
async def approve_post(
    post_id: int,
    service: PostService = Depends(get_post_service),
    current_user = Depends(get_current_user),
):
    return await service.approve_post(post_id, current_user)


@router.post("/{post_id}/reject", response_model=PostOut, summary="Отклонить пост")
async def reject_post(
    post_id: int,
    service: PostService = Depends(get_post_service),
    current_user = Depends(get_current_user),
):
    return await service.reject_post(post_id, current_user)


@router.post("/{post_id}/schedule", response_model=PostOut, summary="Назначить дату публикации")
async def schedule_post(
    post_id: int,
    body: ScheduleRequest,
    service: PostService = Depends(get_post_service),
    current_user = Depends(get_current_user),
):
    return await service.schedule_post(post_id, body.scheduled_at, current_user)




UPLOAD_DIR = "uploads"
ALLOWED_TYPES = {
    "image/jpeg": ("image", ".jpg"),
    "image/png": ("image", ".png"),
    "image/gif": ("image", ".gif"),
    "image/webp": ("image", ".webp"),
    "video/mp4": ("video", ".mp4"),
    "video/webm": ("video", ".webm"),
}

@router.post("/{post_id}/media", response_model=PostOut, summary="Загрузить медиафайл к посту")
async def upload_media(
    post_id: int,
    file: UploadFile = File(...),
    service: PostService = Depends(get_post_service),
    current_user=Depends(get_current_user),
):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Неподдерживаемый тип файла. Разрешены: JPEG, PNG, GIF, WebP, MP4, WebM")

    media_type, ext = ALLOWED_TYPES[file.content_type]
    filename = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    contents = await file.read()
    if len(contents) > 50 * 1024 * 1024:  # 50 MB
        raise HTTPException(status_code=400, detail="Файл слишком большой. Максимум 50 МБ")

    with open(file_path, "wb") as f:
        f.write(contents)

    file_url = f"/uploads/{filename}"
    return await service.add_media(post_id, file_url, media_type, current_user)


@router.post(
    "/{post_id}/schedule-telegram",
    response_model=TelegramPublicationOut,
    status_code=201,
    summary="Запланировать публикацию в Telegram"
)
async def schedule_telegram(
    post_id: int,
    body: TelegramScheduleRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # Проверяем что пост существует и одобрен
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalars().first()
    if not post:
        raise HTTPException(404, "Пост не найден")
    if post.status_id != 3:  # STATUS_APPROVED
        raise HTTPException(400, "Публиковать можно только одобренные посты")
    if post.author_id != current_user.id and current_user.role_id != 1:
        raise HTTPException(403, "Нет доступа")

    scheduled_at = body.scheduled_at
    if scheduled_at.tzinfo is not None:
        scheduled_at = scheduled_at.replace(tzinfo=None)

    pub = TelegramPublication(
        post_id=post_id,
        chat_id=body.chat_id,
        scheduled_at=scheduled_at,
        status="pending"
    )
    db.add(pub)
    await db.commit()
    await db.refresh(pub)
    return pub


@router.get(
    "/{post_id}/telegram-status",
    response_model=list[TelegramPublicationOut],
    summary="Статус публикаций в Telegram"
)
async def telegram_status(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await db.execute(
        select(TelegramPublication).where(TelegramPublication.post_id == post_id)
    )
    return result.scalars().all()