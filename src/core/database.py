import uuid
from datetime import datetime
from decimal import Decimal
from typing import Annotated
from sqlalchemy import Integer, inspect, TIMESTAMP, func, UUID
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs, AsyncSession
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, declared_attr
from src.core.config import database_url 


engine = create_async_engine(url=database_url, echo=False)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
str_uniq = Annotated[str, mapped_column(unique=True, nullable=False)]


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now()
    )

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + "s"
    

    def to_dict(self, exclude_none: bool = False):
        """
        Convert the SQLAlchemy model instance to a dictionary.
        """
        result = {}

        for column in inspect(self.__class__).columns:
            value = getattr(self, column.key)

            if isinstance(value, datetime):
                value = value.isoformat()
            elif isinstance(value, Decimal):
                value = float(value)
            elif isinstance(value, uuid.UUID):
                value = str(value)

            if not exclude_none or value is not None:
                result[column.key] = value
        
        return result
    

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.id}, created_at={self.created_at}, updated_at={self.updated_at})>"


class UUIDBase(Base):
    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        unique=True,
        nullable=False,
        primary_key=True,
        default=uuid.uuid4
    )