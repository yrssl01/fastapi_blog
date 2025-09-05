from typing import Annotated
from datetime import timedelta
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from src.api.dependencies import SessionDep, CurrentUser
from src.schemas.auth import Token
from src.core.config import settings
from src.core.security import create_access_token
from src import crud


router = APIRouter(tags=["login"])


@router.post("/login")
def login(
    session: SessionDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()] 
) -> Token:
    user = crud.authenticate(
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