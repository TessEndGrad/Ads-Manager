from fastapi import HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator

# Импортируем фабрику сессий, настроенную в твоем database.py
from app.database import async_session_maker 

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Инжектирует асинхронную сессию PostgreSQL в каждый запрос.
    Гарантированно закрывает сессию после отправки ответа клиенту.
    """
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_current_user(db: AsyncSession = Depends(get_db)):
    """
    Заглушка для системы авторизации (JWT / Сессии).
    Возвращает временного mock-пользователя с id=1, чтобы
    ручки черновиков и удаления постов работали прямо сейчас.
    """
    class MockUser:
        id = 1
        username = "daniil_dev"
        role_id = 1  # ID роли (например, Администратор)

    return MockUser()