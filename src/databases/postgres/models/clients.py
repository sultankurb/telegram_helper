from sqlalchemy import BigInteger, Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from src.databases.postgres.models.base import BaseORM


class ClientsORM(BaseORM):
    __tablename__ = "clients"
    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    phone_number: Mapped[str] = mapped_column(String)
    full_name: Mapped[str] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(Boolean)
