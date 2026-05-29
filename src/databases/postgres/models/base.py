from datetime import datetime
from uuid import UUID, uuid7

from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy import func


class BaseORM(DeclarativeBase):
    __abstract__ = True
    pk: Mapped[UUID] = mapped_column(primary_key=True, default=uuid7())
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now())
