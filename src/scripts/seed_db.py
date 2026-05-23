"""
Заполняет БД начальными данными: роли, статусы, типы постов, тестовые юзеры.
Запуск: python -m src.scripts.seed_db
"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import engine, Base, async_session_maker
from src.infrastructure.persistence.models.models import (
    Role, PostStatus, PostType, User
)
from passlib.context import CryptContext

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_maker() as db:
        # Roles
        for name in ["manager", "user"]:
            db.add(Role(name=name))
        await db.commit()

        # Post statuses
        for name in ["draft", "moderation", "approved", "published", "rejected"]:
            db.add(PostStatus(name=name))
        await db.commit()

        # Post types
        for name in ["image", "video", "text"]:
            db.add(PostType(name=name))
        await db.commit()

        # Demo users
        db.add(User(username="manager", email="manager@demo.ru",
                    password_hash=pwd.hash("123456"), role_id=1))
        db.add(User(username="user1", email="user@demo.ru",
                    password_hash=pwd.hash("123456"), role_id=2))
        await db.commit()

        print("Seed completed!")


asyncio.run(seed())
