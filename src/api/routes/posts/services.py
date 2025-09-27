from uuid import UUID
from slugify import slugify
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.routes.categories import services as categories_services
from src.api.routes.categories.exceptions import CategoryNotFoundException
from src.models.categories import Category
from src.models.tags import Tag
from src.models.posts import Post
from src.schemas.posts import (
    PostPublic, 
    PostCreate, 
    PostsPublic
)


async def get_or_create_tag(session: AsyncSession, tag_name: str) -> Tag:
    statement = select(Tag).where(Tag.name == tag_name)
    tag = await session.execute(statement)
    tag = tag.scalar_one_or_none()
    if not tag:
        tag = Tag(name=tag_name)
        session.add(tag)
        await session.commit()
        await session.refresh(tag)
    return tag


async def create_post(*, session: AsyncSession, post_create: PostCreate, owner_id: UUID):
    category = await categories_services.get_category_by_id(session=session, id=post_create.category_id)
    if not category.is_active:
        raise CategoryNotFoundException
    slug = slugify(post_create.title)
    db_post = Post(
        **post_create.model_dump(exclude={"slug", "tag_names"}), slug=slug, owner_id=owner_id
    )
    for tag_name in post_create.tag_names:
        tag = await get_or_create_tag(session, tag_name.strip().lower())
        db_post.tags.append(tag)
    
    session.add(db_post)
    await session.commit()
    await session.refresh(db_post)
    return db_post


async def get_posts(session: AsyncSession, skip: int = 0, limit: int = 100):
    statement = select(Post).offset(skip).limit(limit)
    posts = await session.execute(statement)
    posts = posts.scalars().all()
    return PostsPublic(data=posts)


async def get_post(session: AsyncSession, post_id: int) -> Post:
    statement = select(Post).where(Post.id == post_id)
    post = await session.execute(statement)
    post = post.scalar_one_or_none()
    return post


async def add_tags_to_post(session: AsyncSession, post_id: int, tag_names: list[str]) -> Post | None:
    post = await get_post(session, post_id)
    if post:
        return None
    
    for tag_name in tag_names:
        tag = await get_or_create_tag(session, tag_name.strip().lower())
        if tag not in post.tags:
            post.tags.append(tag)
    
    await session.commit()
    await session.refresh(post)
    return post