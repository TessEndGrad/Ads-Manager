from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload


from src.api.v1.dependencies import get_user_service
from src.api.v1.schemas.user import UserOut
from src.core.dependencies import get_current_user, get_db
from src.modules.users.service import UserService
from src.infrastructure.persistence.models.models import User

router = APIRouter(prefix="/users", tags=["Пользователи"])


@router.get("/me", response_model=UserOut, summary="Мой профиль")
async def get_me(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User)
        .where(User.id == current_user.id)
        .options(selectinload(User.role))
    )
    return result.scalar_one()


@router.get("/{user_id}", response_model=UserOut, summary="Пользователь по ID")
async def get_user(
    user_id: int,
    service: UserService = Depends(get_user_service),
    current_user = Depends(get_current_user),
):
    return await service.get_by_id(user_id)


@router.get("/", response_model=list[UserOut], summary="Все пользователи (админ)")
async def get_users(
    service: UserService = Depends(get_user_service),
    current_user = Depends(get_current_user),
):
    return await service.get_all(current_user)
