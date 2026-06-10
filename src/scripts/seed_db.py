import asyncio
from sqlalchemy import select
from src.core.database import engine, Base, async_session_maker
from src.infrastructure.persistence.models.models import Role, PostStatus, PostType, User
from passlib.context import CryptContext

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_maker() as db:
        # Roles
        for name in ["manager", "user"]:
            exists = await db.execute(select(Role).where(Role.name == name))
            if not exists.scalars().first():
                db.add(Role(name=name))
        await db.commit()

        # Post statuses
        for name in ["draft", "moderation", "approved", "published", "rejected"]:
            exists = await db.execute(select(PostStatus).where(PostStatus.name == name))
            if not exists.scalars().first():
                db.add(PostStatus(name=name))
        await db.commit()

        # Post types
        for name in ["image", "video", "text"]:
            exists = await db.execute(select(PostType).where(PostType.name == name))
            if not exists.scalars().first():
                db.add(PostType(name=name))
        await db.commit()

        # Default users
        for username, email, role_id in [
            ("manager", "manager@demo.ru", 1),
            ("user1",   "user@demo.ru",    2),
        ]:
            exists = await db.execute(select(User).where(User.username == username))
            if not exists.scalars().first():
                db.add(User(
                    username=username,
                    email=email,
                    password_hash=pwd.hash("123456"),
                    role_id=role_id,
                ))
        await db.commit()
        print("Seed completed!")

asyncio.run(seed())