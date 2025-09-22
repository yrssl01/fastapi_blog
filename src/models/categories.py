from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import URL
from src.core.database import Base, str_uniq


class Category(Base):
    __tablename__ = "categories"

    name: Mapped[str_uniq]
    description: Mapped[str] = mapped_column(nullable=True)
    slug: Mapped[str_uniq]
    icon: Mapped[str] = mapped_column(nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    