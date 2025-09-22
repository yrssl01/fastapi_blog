from slugify import slugify
from fastapi import APIRouter, Depends, HTTPException
from src.api.dependencies import SessionDep, CurrentUser, get_current_active_superuser, CurrentUserOrNone
from src.api.routes.categories import services
from src.schemas.posts import (
    CategoriesPublic, 
    CategoryPublic, 
    CategoryCreate, 
    CategoryUpdate
)
from src.models.users import User
from src.api.routes.categories.exceptions import CategoryNotFoundException


router = APIRouter(prefix="/categories", tags=["categories"])


@router.post('/', status_code=201, dependencies=[Depends(get_current_active_superuser)])
async def create_category(session: SessionDep, category_in: CategoryCreate):
    category_create = CategoryCreate(**category_in.model_dump())
    category = await services.create_category(session=session, category_create=category_create)
    return category


@router.get('/', response_model=CategoriesPublic)
async def get_categories(
    session: SessionDep, 
    current_user: CurrentUserOrNone, 
    skip: int = 0, 
    limit: int = 100
):
    if current_user and current_user.is_superuser:
        categories_public = await services.get_categories_list(session, skip, limit)
    else:
        categories_public = await services.get_active_categories_list(session, skip, limit)
    return categories_public


@router.get('/{slug}', response_model=CategoryPublic)
async def get_category_by_slug(slug: str, session: SessionDep, current_user: CurrentUserOrNone):
    category = await services.get_category_by_slug(session=session, slug=slug)
    if not category:
        raise CategoryNotFoundException
    if not category.is_active:
        if not current_user or not current_user.is_superuser:
            raise CategoryNotFoundException
    return category


@router.patch('/{id}', response_model=CategoryPublic, dependencies=[Depends(get_current_active_superuser)])
async def update_category(category_id: int, session: SessionDep, category_in: CategoryUpdate):
    category = await services.get_category_by_id(session=session, id=category_id)
    if not category:
        raise CategoryNotFoundException
    category_data = category_in.model_dump(exclude_unset=True)
    if "name" in category_data:
        category.name = category_data["name"]
        category.slug = slugify(category_data["name"])
        category_data.pop("name")
    
    for field, value in category_data.items():
        setattr(category, field, value)
    
    session.add(category)
    await session.commit()
    await session.refresh(category)
    return category




