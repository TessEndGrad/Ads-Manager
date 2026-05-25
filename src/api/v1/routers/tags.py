from fastapi import APIRouter, Depends

from src.api.v1.dependencies import get_tag_repository
from src.api.v1.schemas.tag import TagOut, TagCreate, PopularTagOut
from src.core.dependencies import get_current_user
from src.infrastructure.persistence.models.models import Tag
from src.infrastructure.persistence.repositories.user_repository import TagRepository

router = APIRouter(prefix="/tags", tags=["Теги"])


@router.get("/", response_model=list[PopularTagOut], summary="Популярные теги")
async def get_tags(
    limit: int = 10,
    repo: TagRepository = Depends(get_tag_repository),
    current_user = Depends(get_current_user),
):
    rows = await repo.get_popular(limit)
    return [PopularTagOut(id=tag.id, name=tag.name, posts_count=count) for tag, count in rows]


@router.post("/", response_model=TagOut, status_code=201, summary="Создать тег")
async def create_tag(
    data: TagCreate,
    repo: TagRepository = Depends(get_tag_repository),
    current_user = Depends(get_current_user),
):
    existing = await repo.get_by_name(data.name)
    if existing:
        return existing
    tag = Tag(name=data.name)
    return await repo.create(tag)
