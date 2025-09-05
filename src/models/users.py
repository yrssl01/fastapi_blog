from sqlalchemy.orm import Mapped, mapped_column
from src.core.database import UUIDBase, str_uniq


class User(UUIDBase):
    __tablename__ = "users"

    username: Mapped[str_uniq]
    email: Mapped[str_uniq]
    full_name: Mapped[str | None] = None
    password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    is_superuser: Mapped[bool] = mapped_column(default=False)