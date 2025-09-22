import uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from src.core.database import Base, str_uniq
from src.schemas.posts import PostStatusEnum
from src.models.categories import Category
from src.models.users import User
from src.models.tags import post_tags


class Post(Base):
    __tablename__ = "posts"

    title: Mapped[str] = mapped_column(nullable=False)
    slug: Mapped[str_uniq] 
    content: Mapped[str] = mapped_column(nullable=False)
    allow_comment: Mapped[bool] = mapped_column(default=True)
    status: Mapped[PostStatusEnum] = mapped_column(default=PostStatusEnum.DRAFT)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id", ondelete="SET NULL"))
    category = relationship("Category", lazy="selectin")
    owner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="SET NULL")) 
    owner = relationship("User", lazy="selectin")
    tags = relationship("Tag", secondary=post_tags, back_populates="posts")