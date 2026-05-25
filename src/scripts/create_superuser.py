"""
Создаёт суперпользователя (менеджера).
Запуск: python -m src.scripts.create_superuser
"""
import asyncio
from src.core.database import async_session_maker
from src.infrastructure.persistence.models.models import User
from passlib.context import CryptContext

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def main():
    username = input("Username: ")
    email    = input("Email: ")
    password = input("Password: ")

    async with async_session_maker() as db:
        user = User(
            username=username,
            email=email,
            password_hash=pwd.hash(password),
            role_id=1,
        )
        db.add(user)
        await db.commit()
        print(f"Superuser '{username}' created!")


asyncio.run(main())
