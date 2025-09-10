from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.config import settings
from src import crud
from src.models.users import User
from src.schemas.users import UserCreate


async def init_db(session: AsyncSession):
    user = await session.execute(select(User).where(User.email == settings.FIRST_SUPERUSER))
    user = user.first()
    if not user:
        user_in = UserCreate(
            username=settings.FIRST_SUPERUSER_USERNAME,
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
            is_verified=True
        )
        user = await crud.create_user(session=session, user_create=user_in)