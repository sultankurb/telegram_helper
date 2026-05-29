from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger
from src.databases.postgres.models.base import BaseORM


class AdminsORM(BaseORM):
    __tablename__ = "admins"
    telegram_pk: Mapped[int] = mapped_column(BigInteger, unique=True)
