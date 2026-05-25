from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import func, desc
from app.models import Post, Tag, PostTag, SocialAccount
from typing import List, Optional

class PostRepository:
    @staticmethod
    async def get_by_id(db: AsyncSession, post_id: int) -> Optional[Post]:
        """Получить один пост по ID со всеми медиа и тегами"""
        stmt = (
            select(Post)
            .where(Post.id == post_id)
            .options(selectinload(Post.tags), selectinload(Post.media))
        )
        result = await db.execute(stmt)
        return result.scalars().first()

    @staticmethod
    async def get_user_drafts(db: AsyncSession, user_id: int, draft_status_id: int) -> List[Post]:
        """Получить черновики конкретного пользователя, отсортированные по дате создания"""
        stmt = (
            select(Post)
            .where(Post.author_id == user_id, Post.status_id == draft_status_id)
            .options(selectinload(Post.tags), selectinload(Post.media))
            .order_by(desc(Post.created_at))
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def delete_post(db: AsyncSession, post: Post) -> None:
        """Удалить пост из базы данных"""
        await db.delete(post)
        await db.commit()


class TagRepository:
    @staticmethod
    async def get_popular_tags(db: AsyncSession, limit: int = 10):
        """Получить список тегов с подсчетом их упоминаний в постах"""
        stmt = (
            select(Tag, func.count(PostTag.post_id).label("posts_count"))
            .join(PostTag, Tag.id == PostTag.tag_id, isouter=True)
            .group_by(Tag.id)
            .order_by(desc("posts_count"))
            .limit(limit)
        )
        result = await db.execute(stmt)
        return result.all()


class IntegrationRepository:
    @staticmethod
    async def get_telegram_status(db: AsyncSession, user_id: int) -> List[SocialAccount]:
        """Получить все привязанные аккаунты Telegram для конкретного пользователя"""
        stmt = select(SocialAccount).where(
            SocialAccount.user_id == user_id,
            SocialAccount.platform == "Telegram"
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())