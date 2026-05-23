from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.dependencies import get_db
from src.infrastructure.persistence.repositories.post_repository import PostRepository
from src.infrastructure.persistence.repositories.user_repository import UserRepository, TagRepository
from src.modules.posts.service import PostService
from src.modules.users.service import UserService


def get_post_service(db: AsyncSession = Depends(get_db)) -> PostService:
    return PostService(PostRepository(db), TagRepository(db))


def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(UserRepository(db))


def get_tag_repository(db: AsyncSession = Depends(get_db)) -> TagRepository:
    return TagRepository(db)
