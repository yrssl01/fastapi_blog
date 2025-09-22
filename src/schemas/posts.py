from pydantic import BaseModel, Field, HttpUrl
from enum import Enum


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=200)
    icon: HttpUrl | None = Field(default=None, max_length=150)
    is_active: bool = True


class TagBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=30)


class CategoryPublic(CategoryBase):
    id: int
    slug: str
    # post_count: int

    class Config: 
        from_attributes = True


class CategoriesPublic(BaseModel):
    data: list[CategoryPublic]
    count: int


class TagCreate(TagBase):
    slug: str = Field(..., min_length=1, max_length=30)


class CategoryCreate(CategoryBase):
    slug: str | None = Field(default=None, min_length=1, max_length=100)


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=200)
    icon: HttpUrl | None = Field(default=None, max_length=150)
    is_active: bool | None = None
    slug: str | None = Field(default=None, min_length=1, max_length=100)


class TagPublic(TagBase):
    id: int
    # post_count: int

    class Config:
        from_attributes = True  


class PostStatusEnum(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class PostBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    allow_comments: bool = True


class PostCreate(PostBase):
    status: PostStatusEnum = PostStatusEnum.DRAFT
    category_id: CategoryPublic
    tag_ids: list[TagPublic] = Field(default=[], max_items=7)


# class PostUpdate(BaseModel):
#     title: str
    

class PostPublic(PostBase):
    id: int
    slug: str

