from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from sqlalchemy import select, func, asc, desc, Column
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.infrastructure.persistence.models.models import Post, post_tags_table


@dataclass
class PostFilters:
    status_id:      Optional[int]      = None
    post_type_id:   Optional[int]      = None
    author_id:      Optional[int]      = None
    tag_ids:        list[int]          = field(default_factory=list)
    scheduled_from: Optional[datetime] = None
    scheduled_to:   Optional[datetime] = None
    created_from:   Optional[datetime] = None
    created_to:     Optional[datetime] = None
    search:         Optional[str]      = None


SORTABLE_FIELDS: dict = {
    "created_at":   Post.created_at,
    "updated_at":   Post.updated_at,
    "scheduled_at": Post.scheduled_at,
    "title":        Post.title,
    "status_id":    Post.status_id,
}


class PostRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_list(
        self,
        filters: PostFilters,
        order_by: str = "created_at",
        order_dir: str = "desc",
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Post], int]:
        query = (
            select(Post)
            .options(
                selectinload(Post.tags),
                selectinload(Post.media_items),
                selectinload(Post.status),
                selectinload(Post.post_type),
            )
        )

        if filters.status_id is not None:
            query = query.where(Post.status_id == filters.status_id)
        if filters.post_type_id is not None:
            query = query.where(Post.post_type_id == filters.post_type_id)
        if filters.author_id is not None:
            query = query.where(Post.author_id == filters.author_id)
        if filters.search:
            pattern = f"%{filters.search}%"
            query = query.where(Post.title.ilike(pattern) | Post.content.ilike(pattern))
        if filters.scheduled_from:
            query = query.where(Post.scheduled_at >= filters.scheduled_from)
        if filters.scheduled_to:
            query = query.where(Post.scheduled_at <= filters.scheduled_to)
        if filters.created_from:
            query = query.where(Post.created_at >= filters.created_from)
        if filters.created_to:
            query = query.where(Post.created_at <= filters.created_to)

        for tag_id in filters.tag_ids:
            query = query.where(
                Post.id.in_(
                    select(post_tags_table.c.post_id).where(
                        post_tags_table.c.tag_id == tag_id
                    )
                )
            )

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self._session.execute(count_query)
        total: int = total_result.scalar_one()

        sort_col = SORTABLE_FIELDS.get(order_by, Post.created_at)
        sort_expr = asc(sort_col) if order_dir == "asc" else desc(sort_col)
        query = query.order_by(sort_expr)

        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)

        result = await self._session.execute(query)
        posts = list(result.scalars().unique().all())
        return posts, total

    async def get_by_id(self, post_id: int) -> Optional[Post]:
        query = (
            select(Post)
            .where(Post.id == post_id)
            .options(
                selectinload(Post.tags),
                selectinload(Post.media_items),
                selectinload(Post.status),
                selectinload(Post.post_type),
                selectinload(Post.approvals),
            )
        )
        result = await self._session.execute(query)
        return result.scalars().first()

    async def create(self, post: Post) -> Post:
        self._session.add(post)
        await self._session.commit()
        # перезапрашиваем с eager-загрузкой всех связей
        return await self.get_by_id(post.id)

    async def update(self, post: Post) -> Post:
        await self._session.commit()
        # перезапрашиваем с eager-загрузкой всех связей
        return await self.get_by_id(post.id)

    async def delete(self, post: Post) -> None:
        await self._session.delete(post)
        await self._session.commit()
