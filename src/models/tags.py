from sqlalchemy import Table, Integer, ForeignKey, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.database import Base


post_tags = Table(
    "post_tags",
    Base.metadata,
    Column('post_id', Integer, ForeignKey('posts.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
)


class Tag(Base):
    __tablename__ = "tags"

    name: Mapped[str] = mapped_column(nullable=False)
    
    posts = relationship("Post", secondary=post_tags)