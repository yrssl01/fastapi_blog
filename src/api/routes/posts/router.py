from fastapi import APIRouter, Depends
from typing import Annotated
from src.api.dependencies import get_current_verified_user, SessionDep, CurrentUser
from src.schemas.posts import PostCreate, PostPublic, PostsPublic
from src.models.posts import Post
from src.models.tags import Tag
from src.api.routes.posts import services


router = APIRouter(prefix="/posts", tags=["posts"])


@router.post("/", status_code=201, dependencies=[Depends(get_current_verified_user)], response_model=PostPublic)
async def create_post(session: SessionDep, post_in: PostCreate, current_user: CurrentUser):
    return await services.create_post(session=session, post_create=post_in, owner_id=current_user.id)


@router.get("/", response_model=PostsPublic)
async def get_posts(session: SessionDep, skip: int = 0, limit: int = 100):
    posts = await services.get_posts(session, skip, limit)
    return posts


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