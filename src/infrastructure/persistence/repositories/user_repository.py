from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.infrastructure.persistence.models.models import User, Tag, post_tags_table
from sqlalchemy import func, desc


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, user_id: int) -> Optional[User]:
        result = await self._session.execute(
            select(User).where(User.id == user_id).options(selectinload(User.role))
        )
        return result.scalars().first()

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self._session.execute(
            select(User).where(User.email == email).options(selectinload(User.role))
        )
        return result.scalars().first()

    async def get_by_username(self, username: str) -> Optional[User]:
        result = await self._session.execute(
            select(User).where(User.username == username)
        )
        return result.scalars().first()

    async def create(self, user: User) -> User:
        self._session.add(user)
        await self._session.commit()
        await self._session.refresh(user)
        return user

    async def get_all(self) -> list[User]:
        result = await self._session.execute(
            select(User).options(selectinload(User.role))
        )
        return list(result.scalars().all())


class TagRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_all(self) -> list[Tag]:
        result = await self._session.execute(select(Tag))
        return list(result.scalars().all())

    async def get_by_id(self, tag_id: int) -> Optional[Tag]:
        result = await self._session.execute(select(Tag).where(Tag.id == tag_id))
        return result.scalars().first()

    async def get_by_name(self, name: str) -> Optional[Tag]:
        result = await self._session.execute(select(Tag).where(Tag.name == name))
        return result.scalars().first()

    async def create(self, tag: Tag) -> Tag:
        self._session.add(tag)
        await self._session.commit()
        await self._session.refresh(tag)
        return tag

    async def get_popular(self, limit: int = 10):
        from src.infrastructure.persistence.models.models import post_tags_table as ptt
        stmt = (
            select(Tag, func.count(ptt.c.post_id).label("posts_count"))
            .outerjoin(ptt, Tag.id == ptt.c.tag_id)
            .group_by(Tag.id)
            .order_by(desc("posts_count"))
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return result.all()
