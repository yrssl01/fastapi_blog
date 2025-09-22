from typing import Annotated
from datetime import timedelta
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from src.api.dependencies import SessionDep, CurrentUser
from src.schemas.auth import Token, NewPassword
from src.schemas.message import Message
from src.core.config import settings
from src.core.security import create_access_token, get_password_hash
from src import crud
from src.utils.tokens import generate_password_reset_token, verify_user_token, generate_email_verification_token
from src.utils.emails import generate_password_reset_email, generate_verification_email, send_email
from src.logger import logger


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
async def login(
    session: SessionDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()] 
) -> Token:
    user = await crud.authenticate(
        session=session,
        email=form_data.username,
        password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return Token(
        access_token=create_access_token(
            user.id,
            expires_delta=access_token_expires
        )
    )


@router.post("/password-recovery/{email}")
async def recover_password(email: str, session: SessionDep) -> Message:
    user = await crud.get_user_by_email(session=session, email=email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The user with this email does not exist in the system.",
        )
    password_reset_token = generate_password_reset_token(email=email)
    email_data = generate_password_reset_email(
        email_to=user.email,
        email=user.email,
        token=password_reset_token
    )
    send_email(
        email_to=user.email,
        subject=email_data.subject,
        html_content=email_data.html_content
    )
    logger.info(f"Password recovery email sent to {user.email}")
    return Message(message="Password recovery email sent")


@router.post("/reset-password/")
async def reset_password(session: SessionDep, body: NewPassword) -> Message:
    email = verify_user_token(token=body.token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")
    user = await crud.get_user_by_email(session=session, email=email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    hashed_password = get_password_hash(body.new_password)
    user.password = hashed_password
    await session.commit()
    await session.refresh(user)
    logger.info(f"User {user.username} had reset and updated password")
    return Message(message="Password updated successfully")


@router.post("/request-email-verification/")
async def request_email_for_verification(current_user: CurrentUser) -> Message:
    if current_user.is_verified:
        raise HTTPException(status_code=409, detail="User is already verified")
    email = current_user.email
    email_verification_token = generate_email_verification_token(email=email)
    email_data = generate_verification_email(
        email_to=email,
        email=email,
        token=email_verification_token
    )
    send_email(
        email_to=email,
        subject=email_data.subject,
        html_content=email_data.html_content
    )
    logger.info(f"Email verification sent to {email}")
    return Message(message="Email verification sent to user email")



@router.post("/verify-email/")
async def verify_email(session: SessionDep, token: str) -> Message:
    email = verify_user_token(token=token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")
    user = await crud.get_user_by_email(session=session, email=email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    if user.is_verified:
        raise HTTPException(status_code=409, detail="User is already verified")
    user.is_verified = True
    await session.commit()
    await session.refresh(user)
    logger.info(f"User {user.username} had confirmed his email")
    return Message(message="User confirmed his email and now is verified")