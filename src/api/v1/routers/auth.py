from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.dependencies import get_user_service
from src.api.v1.schemas.user import UserRegister, UserLogin, TokenResponse, UserOut
from src.modules.users.service import UserService
from src.infrastructure.persistence.models.models import User
from src.core.dependencies import get_db

router = APIRouter(prefix="/auth", tags=["Авторизация"])


@router.post("/register", response_model=UserOut, status_code=201, summary="Регистрация")
async def register(
    data: UserRegister,
    service: UserService = Depends(get_user_service),
    db: AsyncSession = Depends(get_db),
):
    user = await service.register(data.username, data.email, data.password)
    result = await db.execute(
        select(User)
        .where(User.id == user.id)
        .options(selectinload(User.role))
    )
    return result.scalar_one()


@router.post("/login", response_model=TokenResponse, summary="Вход")
async def login(data: UserLogin, service: UserService = Depends(get_user_service)):
    token = await service.login(data.email, data.password)
    return TokenResponse(access_token=token)