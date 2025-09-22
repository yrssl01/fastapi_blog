from slugify import slugify
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.categories import Category
from src.schemas.posts import PostPublic, PostCreate


async def create_post(*, session: AsyncSession, post_create: PostCreate):
    slug = slugify(post_create.name)
    db_post = Category(
        **post_create.model_dump(exclude={"slug"}), slug=slug
    )
    session.add(db_post)
    await session.commit()
    await session.refresh(db_post)
    return db_post


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
