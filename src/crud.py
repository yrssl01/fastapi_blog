import uuid
from typing import Any
from sqlalchemy import select
from sqlalchemy.orm import Session
from src.core.security import get_password_hash, verify_password
from src.schemas.users import UserCreate
from src.models.users import User


def create_user(*, session: Session, user_create: UserCreate):
    hashed_password = get_password_hash(user_create.password)
    db_user = User(
        **user_create.model_dump(exclude={"password"}), password=hashed_password
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user_by_email(*, session: Session, email:str) -> User | None:
    statement = select(User).where(User.email == email)
    session_user = session.execute(statement).scalars().first()
    return session_user


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.password):
        return None
    return db_user