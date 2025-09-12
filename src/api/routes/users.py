from src.logger import logger
from src.api.dependencies import CurrentUser, SessionDep, get_current_active_superuser, get_current_verified_user
from src import crud
import uuid
from typing import Any
from sqlalchemy import select, func, update
from sqlalchemy.exc import SQLAlchemyError
from src.core.config import settings
from src.utils.tokens import generate_email_verification_token
from src.utils.emails import send_email, generate_verification_email
from src.core.security import get_password_hash, verify_password
from src.models.users import User
from src.schemas.users import (
    UserRegister, 
    UserCreate,
    UserUpdate, 
    UserUpdateMe,
    UserPublic,
    UsersPublic,
    UpdatePassword
)
from src.schemas.message import Message
from fastapi import APIRouter, HTTPException, status, Depends


router = APIRouter(tags=["users"])


@router.get("/", response_model=UsersPublic, dependencies=[Depends(get_current_active_superuser)])
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


@router.get("/{user_id}", response_model=UserPublic)
async def read_user_by_id(user_id: uuid.UUID, session: SessionDep, current_user: CurrentUser):
    user = await session.get(User, user_id)
    if user == current_user:
        return user
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )
    return user


@router.patch("/me", response_model=UserPublic, dependencies=[Depends(get_current_verified_user)])
async def update_user_me(*, session: SessionDep, user_in: UserUpdateMe, current_user: CurrentUser):
    if user_in.email:
        existing_user = await crud.get_user_by_email(session=session, email=user_in.email)
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )
    user_data = user_in.model_dump(exclude_unset=True)
    try: 
        db_user = await session.get(User, current_user.id)
        for field, value in user_data.items():
            setattr(db_user, field, value)
        await session.commit()
        await session.refresh(db_user)
        return db_user
    except Exception as e:
        logger.error(f"Error updating user {current_user.id}: {e}")
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.patch("/me/password", response_model=Message)
async def update_user_password_me(*, session: SessionDep, body: UpdatePassword, current_user: CurrentUser):
    if not verify_password(body.current_password, current_user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect password")
    if body.current_password == body.new_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New password cannot be the same as the current password")
    hashed_password = get_password_hash(body.new_password)
    current_user.password = hashed_password
    await session.commit()
    await session.refresh(current_user)
    return Message(message="Password updated successfully")


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
    email_verification_token = generate_email_verification_token(email=user.email) 
    email_data = generate_verification_email(email_to=user.email, email=user.email, token=email_verification_token)
    send_email(
        email_to=user.email,
        subject=email_data.subject,
        html_content=email_data.html_content
    )
    logger.info(f"New user registered: {user.username} ({user.id}), and verification email is sent to {user.email}")
    return user