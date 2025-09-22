from fastapi import APIRouter, Depends
from typing import Annotated
from src.api.dependencies import get_current_verified_user, SessionDep, CurrentUser
from src.models.posts import Post


router = APIRouter(tags=["posts"])


@router.post("/", status_code=201, dependencies=[Depends(get_current_verified_user)])
async def create_post(session: SessionDep, current_user: CurrentUser):
    pass # todo


@router.get("/")
async def get_posts():
    pass # todo


@router.get("/my")
async def get_my_posts():
    pass # todo


@router.get("/{post_id}")
async def get_post():
    pass # todo


@router.get("/{user_id}")
async def get_user_posts():
    pass # todo

@router.patch("/{post_id}")
async def update_post():
    pass # todo