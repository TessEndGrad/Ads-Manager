from datetime import datetime, timedelta

from fastapi import HTTPException
from jose import jwt
from passlib.context import CryptContext

from src.core.config import settings
from src.infrastructure.persistence.models.models import User
from src.infrastructure.persistence.repositories.user_repository import UserRepository

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

DEFAULT_ROLE_ID = 2  # обычный пользователь


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(user_id: int) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"sub": str(user_id), "exp": expire}, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


class UserService:
    def __init__(self, repo: UserRepository) -> None:
        self._repo = repo

    async def register(self, username: str, email: str, password: str) -> User:
        if await self._repo.get_by_email(email):
            raise HTTPException(status_code=400, detail="Email уже занят")
        if await self._repo.get_by_username(username):
            raise HTTPException(status_code=400, detail="Имя пользователя уже занято")
        user = User(
            username=username,
            email=email,
            password_hash=hash_password(password),
            role_id=DEFAULT_ROLE_ID,
        )
        return await self._repo.create(user)

    async def login(self, email: str, password: str) -> str:
        user = await self._repo.get_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(status_code=401, detail="Неверный email или пароль")
        return create_access_token(user.id)

    async def get_me(self, current_user) -> User:
        return current_user

    async def get_by_id(self, user_id: int) -> User:
        user = await self._repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        return user

    async def get_all(self, current_user) -> list[User]:
        if current_user.role_id != 1:
            raise HTTPException(status_code=403, detail="Только администратор")
        return await self._repo.get_all()
