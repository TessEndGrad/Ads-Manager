from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import datetime

# Импорты зависимостей, схем и репозиториев
from app.dependency import get_db, get_current_user
from app.schemas import PostResponse, PopularTagResponse, IntegrationStatusResponse
from app.repository.posts import PostRepository, TagRepository, IntegrationRepository

router = APIRouter(prefix="/v1", tags=["Operations API"])

# ID статуса "Черновик" из таблицы post_statuses
DRAFT_STATUS_ID = 1


# 1. GET /api/v1/posts/{post_id} — Получить один пост по ID
@router.get("/posts/{post_id}", response_model=PostResponse)
async def get_post(post_id: int, db: AsyncSession = Depends(get_db)):
    post = await PostRepository.get_by_id(db, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Пост не найден"
        )
    return post


# 2. DELETE /api/v1/posts/{post_id} — Удалить пост
@router.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    post = await PostRepository.get_by_id(db, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Пост не найден"
        )
    
    # Проверка бизнес-логики: только создатель может удалить свой пост
    if post.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Вы не являетесь автором этого поста, доступ запрещен"
        )
        
    await PostRepository.delete_post(db, post)
    return None


# 3. GET /api/v1/posts/my-drafts — Получить мои черновики
@router.get("/posts/my-drafts", response_model=List[PostResponse])
async def get_my_drafts(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return await PostRepository.get_user_drafts(
        db, 
        user_id=current_user.id, 
        draft_status_id=DRAFT_STATUS_ID
    )


# 4. GET /api/v1/integrations/status — Статус интеграций Telegram
@router.get("/integrations/status", response_model=List[IntegrationStatusResponse])
async def get_telegram_integration_status(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    accounts = await IntegrationRepository.get_telegram_status(db, user_id=current_user.id)
    
    result = []
    for acc in accounts:
        # Проверяем, активен ли токен по дате истечения
        is_active = True
        if acc.expires_at and acc.expires_at < datetime.utcnow():
            is_active = False
            
        result.append(
            IntegrationStatusResponse(
                account_name=acc.account_name,
                platform=acc.platform,
                is_active=is_active,
                expires_at=acc.expires_at
            )
        )
    return result


# 5. GET /api/v1/tags — Получить популярные теги
@router.get("/tags", response_model=List[PopularTagResponse])
async def get_popular_tags(limit: int = 10, db: AsyncSession = Depends(get_db)):
    tags_data = await TagRepository.get_popular_tags(db, limit=limit)
    
    return [
        PopularTagResponse(
            id=tag.id,
            name=tag.name,
            posts_count=posts_count
        )
        for tag, posts_count in tags_data
    ]