from sqlalchemy import INTEGER, TEXT, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from src.databases.postgres.models.base import BaseORM


class MediaORM(BaseORM):
    __tablename__ = "media"
    pk: Mapped[int] = mapped_column(
        INTEGER,
        primary_key=True,
        autoincrement=True,
    )
    media_url: Mapped[str] = mapped_column(TEXT)
    media_comments: Mapped[str] = mapped_column(TEXT)
    is_premium: Mapped[bool] = mapped_column(
        Boolean, default=False,
    )
