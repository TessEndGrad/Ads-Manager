from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from src.core.dependencies import get_db, get_current_user
from src.infrastructure.persistence.models.models import TelegramPublication, Post
from src.infrastructure.persistence.models.models import TelegramChat
from src.infrastructure.persistence.models.models import TelegramChannel

router = APIRouter(prefix="/telegram", tags=["Telegram"])


@router.get("/channels")
async def get_telegram_channels(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Получить список каналов пользователя"""
    result = await db.execute(
        select(TelegramChannel).where(
            TelegramChannel.user_id == current_user.id
        )
    )
    channels = result.scalars().all()
    return [
        {"id": c.id, "chat_id": c.chat_id, "title": c.title, "chat_type": c.chat_type}
        for c in channels
    ]

@router.post("/channels/register")
async def register_telegram_channel(
    body: dict,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Регистрация канала"""
    # Проверяем, не добавлен ли уже такой канал
    result = await db.execute(
        select(TelegramChannel).where(
            TelegramChannel.chat_id == body["chat_id"],
            TelegramChannel.user_id == current_user.id
        )
    )
    existing = result.scalars().first()
    
    if existing:
        return {"ok": True, "message": "Канал уже добавлен"}
    
    channel = TelegramChannel(
        chat_id=body["chat_id"],
        title=body.get("title", ""),
        chat_type="channel",
        user_id=current_user.id
    )
    db.add(channel)
    await db.commit()
    return {"ok": True}

@router.get("/pending")
async def get_pending_publications(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Возвращает pending публикации у которых время наступило"""
    now = datetime.utcnow()
    result = await db.execute(
        select(TelegramPublication)
        .where(
            TelegramPublication.status == "pending",
            TelegramPublication.scheduled_at <= now,
        )
        .options(
            selectinload(TelegramPublication.post).selectinload(Post.media_items)
        )
    )
    publications = result.scalars().all()
    return [
        {
            "id": p.id,
            "chat_id": p.chat_id,
            "post": {
                "id": p.post.id,
                "title": p.post.title,
                "content": p.post.content,
                "tags": [
                    {"id": t.id, "name": t.name}
                    for t in p.post.tags
                ],
                "media_items": [
                    {"file_url": m.file_url, "media_type": m.media_type}
                    for m in p.post.media_items
                ],
            }
        }
        for p in publications
    ]


@router.patch("/publications/{pub_id}")
async def mark_publication(
    pub_id: int,
    body: dict,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await db.execute(
        select(TelegramPublication).where(TelegramPublication.id == pub_id)
    )
    pub = result.scalars().first()
    if not pub:
        return {"ok": False}
    if body.get("success"):
        pub.status = "done"
        pub.published_at = datetime.utcnow()
    else:
        pub.status = "failed"
        pub.error = body.get("error")
    await db.commit()
    return {"ok": True}


@router.post("/chats/register")
async def register_telegram_chat(
    body: dict,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Регистрация чата, куда добавлен бот"""
    chat = TelegramChat(
        chat_id=body["chat_id"],
        title=body.get("title", ""),
        chat_type=body.get("chat_type", "group"),
        added_by_user_id=current_user.id
    )
    db.add(chat)
    await db.commit()
    return {"ok": True}

@router.get("/chats")
async def get_telegram_chats(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Получить список доступных чатов"""
    result = await db.execute(
        select(TelegramChat).where(
            TelegramChat.added_by_user_id == current_user.id
        )
    )
    chats = result.scalars().all()
    return [
        {"id": c.chat_id, "title": c.title, "type": c.chat_type}
        for c in chats
    ]