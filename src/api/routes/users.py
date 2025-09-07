from src.logger import logger
from src.api.dependencies import CurrentUser, SessionDep, get_current_active_superuser
from src import crud
import uuid
from typing import Any
from sqlalchemy import select, func
from src.core.config import settings
from src.core.security import get_password_hash, verify_password
from src.models.users import User
from src.schemas.users import (
    UserRegister, 
    UserCreate,
    UserUpdate,
    UserPublic,
    UsersPublic
)
from fastapi import APIRouter, HTTPException, status, Depends


router = APIRouter(tags=["users"])


@router.get("/", response_model=list[UserPublic], dependencies=[Depends(get_current_active_superuser)])
async def read_users(session: SessionDep, skip: int = 0, limit: int = 100):
    count_statement = select(func.count()).select_from(User)
    count = await session.execute(count_statement)
    count = count.scalar_one()
    statement = select(User).offset(skip).limit(limit)
    users = await session.execute(statement)
    users = users.scalars().all()
    return UsersPublic(data=users, count=count)



@router.get("/me", response_model=UserPublic)
async def read_users_me(current_user: CurrentUser):
    return current_user


@router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=UserPublic)
async def register_user(session: SessionDep, user_in: UserRegister):
    user = await crud.get_user_by_email(session=session, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    user = await crud.get_user_by_username(session=session, username=user_in.username)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )
    user_create = UserCreate(**user_in.model_dump())
    user = await crud.create_user(session=session, user_create=user_create)
    logger.info(f"New user registered: {user.username} ({user.id})")
    return user