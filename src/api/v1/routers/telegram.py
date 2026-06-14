from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from src.core.dependencies import get_db, get_current_user
from src.infrastructure.persistence.models.models import TelegramPublication, Post

router = APIRouter(prefix="/telegram", tags=["Telegram"])


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