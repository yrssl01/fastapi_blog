from slugify import slugify
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.categories import Category
from src.schemas.posts import CategoriesPublic, CategoryCreate 


async def create_category(*, session: AsyncSession, category_create: CategoryCreate):
    slug = slugify(category_create.name)
    db_category = Category(
        **category_create.model_dump(exclude={"slug"}), slug=slug
    )
    session.add(db_category)
    await session.commit()
    await session.refresh(db_category)
    return db_category


async def get_categories_list(session: AsyncSession, skip: int = 0, limit: int = 100):
    count_statement = select(func.count()).select_from(Category)
    count = await session.execute(count_statement)
    count = count.scalar_one()
    statement = select(Category).offset(skip).limit(limit)
    categories = await session.execute(statement)
    categories = categories.scalars().all()
    return CategoriesPublic(data=categories, count=count)


async def get_active_categories_list(session: AsyncSession, skip: int = 0, limit: int = 100):
    count_statement = select(func.count()).select_from(Category).where(Category.is_active == True)
    count = await session.execute(count_statement)
    count = count.scalar_one()
    statement = select(Category).where(Category.is_active == True).offset(skip).limit(limit)
    categories = await session.execute(statement)
    categories = categories.scalars().all()
    return CategoriesPublic(data=categories, count=count)


async def get_category_by_slug(*, session: AsyncSession, slug: str) -> Category | None:
    statement = select(Category).where(Category.slug == slug)
    session_category = await session.execute(statement)
    session_category = session_category.scalar_one_or_none()
    return session_category


async def get_category_by_id(*, session: AsyncSession, id: int) -> Category | None:
    statement = select(Category).where(Category.id == id)
    session_category = await session.execute(statement)
    session_category = session_category.scalar_one_or_none()
    return session_category
