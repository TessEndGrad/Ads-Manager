"""
Инициализация таблиц в БД (альтернатива alembic для быстрого старта).
Запуск: python -m src.scripts.init_db
"""
import asyncio
from src.core.database import engine, Base
import src.infrastructure.persistence.models.models  # noqa: side effect — registers all models


async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Tables created!")

asyncio.run(main())
