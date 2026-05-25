import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

# Загружаем переменные окружения из файла .env
load_dotenv()

# Получаем URL базы данных. Если его нет в .env, используем дефолтный шаблон для локальной разработки
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+asyncpg://postgres:password@localhost:5432/adds_manager"
)

# 1. Создаем асинхронный движок (Engine) для работы с PostgreSQL через драйвер asyncpg
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Выводит все SQL-запросы в консоль. Удобно для разработки, в продакшене лучше выключить.
)

# 2. Фабрика сессий (Session Maker) — генерирует асинхронные сессии для каждого запроса к API
async_session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False  # Предотвращает автоматическое стирание данных из объектов после коммита
)