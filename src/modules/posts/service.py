from datetime import datetime
from typing import Optional

from fastapi import HTTPException, status

from src.infrastructure.persistence.models.models import Post, Tag
from src.infrastructure.persistence.repositories.post_repository import (
    PostRepository,
    PostFilters,
)
from src.infrastructure.persistence.repositories.user_repository import TagRepository

# ID статусов в БД (seed_db.py заполняет в таком порядке)
STATUS_DRAFT      = 1
STATUS_MODERATION = 2
STATUS_APPROVED   = 3
STATUS_PUBLISHED  = 4
STATUS_REJECTED   = 5

MANAGER_ROLE_ID = 1  # role_id=1 — менеджер/админ


class PostService:
    def __init__(self, repo: PostRepository, tag_repo: TagRepository) -> None:
        self._repo     = repo
        self._tag_repo = tag_repo

    async def get_posts(
        self,
        filters: PostFilters,
        order_by: str,
        order_dir: str,
        page: int,
        page_size: int,
        current_user,
    ) -> tuple[list[Post], int]:
        # Обычный пользователь видит только свои посты
        if current_user.role_id != MANAGER_ROLE_ID:
            filters.author_id = current_user.id
        return await self._repo.get_list(filters, order_by, order_dir, page, page_size)

    async def get_by_id(self, post_id: int, current_user) -> Post:
        post = await self._repo.get_by_id(post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Пост не найден")
        if current_user.role_id != MANAGER_ROLE_ID and post.author_id != current_user.id:
            raise HTTPException(status_code=403, detail="Доступ запрещён")
        return post

    async def create_post(self, data, current_user) -> Post:
        tags = []
        for tag_id in data.tag_ids:
            tag = await self._tag_repo.get_by_id(tag_id)
            if tag:
                tags.append(tag)

        post = Post(
            title=data.title,
            content=data.content,
            author_id=current_user.id,
            post_type_id=data.post_type_id,
            status_id=STATUS_DRAFT,
            scheduled_at=data.scheduled_at,
        )
        post.tags = tags
        return await self._repo.create(post)

    async def update_post(self, post_id: int, data, current_user) -> Post:
        post = await self._repo.get_by_id(post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Пост не найден")
        if post.author_id != current_user.id and current_user.role_id != MANAGER_ROLE_ID:
            raise HTTPException(status_code=403, detail="Нет доступа")
        if post.status_id not in (STATUS_DRAFT, STATUS_REJECTED):
            raise HTTPException(status_code=400, detail="Редактировать можно только черновик или отклонённый пост")

        if data.title is not None:
            post.title = data.title
        if data.content is not None:
            post.content = data.content
        if data.post_type_id is not None:
            post.post_type_id = data.post_type_id

        
        if data.scheduled_at is not None:
            scheduled_at = data.scheduled_at
            if scheduled_at.tzinfo is not None:
                scheduled_at = scheduled_at.replace(tzinfo=None)
            post.scheduled_at = scheduled_at

        if data.tag_ids is not None:
            tags = []
            for tag_id in data.tag_ids:
                tag = await self._tag_repo.get_by_id(tag_id)
                if tag:
                    tags.append(tag)
            post.tags = tags

        return await self._repo.update(post)

    async def delete_post(self, post_id: int, current_user) -> None:
        post = await self._repo.get_by_id(post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Пост не найден")
        if post.author_id != current_user.id and current_user.role_id != MANAGER_ROLE_ID:
            raise HTTPException(status_code=403, detail="Доступ запрещён")
        await self._repo.delete(post)

    async def submit_post(self, post_id: int, current_user) -> Post:
        post = await self._repo.get_by_id(post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Пост не найден")
        if post.author_id != current_user.id:
            raise HTTPException(status_code=403, detail="Доступ запрещён")
        if post.status_id != STATUS_DRAFT:
            raise HTTPException(status_code=400, detail="Только черновик можно отправить на модерацию")
        post.status_id = STATUS_MODERATION
        return await self._repo.update(post)

    async def approve_post(self, post_id: int, current_user) -> Post:
        if current_user.role_id != MANAGER_ROLE_ID:
            raise HTTPException(status_code=403, detail="Только менеджер может одобрять посты")
        post = await self._repo.get_by_id(post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Пост не найден")
        if post.status_id != STATUS_MODERATION:
            raise HTTPException(status_code=400, detail="Пост не на модерации")
        post.status_id = STATUS_APPROVED
        return await self._repo.update(post)

    async def reject_post(self, post_id: int, current_user) -> Post:
        if current_user.role_id != MANAGER_ROLE_ID:
            raise HTTPException(status_code=403, detail="Только менеджер может отклонять посты")
        post = await self._repo.get_by_id(post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Пост не найден")
        if post.status_id != STATUS_MODERATION:
            raise HTTPException(status_code=400, detail="Пост не на модерации")
        post.status_id = STATUS_REJECTED
        return await self._repo.update(post)

    async def schedule_post(self, post_id: int, scheduled_at: datetime, current_user) -> Post:
        post = await self._repo.get_by_id(post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Пост не найден")
        if post.author_id != current_user.id and current_user.role_id != MANAGER_ROLE_ID:
            raise HTTPException(status_code=403, detail="Доступ запрещён")
        post.scheduled_at = scheduled_at
        return await self._repo.update(post)

    async def get_my_drafts(self, current_user) -> list[Post]:
        filters = PostFilters(author_id=current_user.id, status_id=STATUS_DRAFT)
        posts, _ = await self._repo.get_list(filters, "created_at", "desc", 1, 100)
        return posts
