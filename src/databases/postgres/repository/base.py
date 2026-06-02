from typing import Any, Sequence, TypeVar

from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


class SQLAlchemyRepository:
    def __init__(self, session_pool: AsyncSession, model: type[T]):
        self.model = model
        self.session = session_pool

    async def select_all(
        self, limit: int = 100, offset: int = 0
    ) -> Sequence[T]:
        stmt = select(self.model).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def select_one(self, filters: dict[str, Any]) -> T | None:
        stmt = select(self.model).filter_by(**filters)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def insert_one(self, data: dict[str, Any]):
        stmt = insert(self.model).values(**data).returning(self.model)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete_one(self, filters: dict[str, Any]) -> None:
        query = delete(self.model).filter_by(**filters)
        await self.session.execute(query)

    async def update_one(
        self, values: dict[str, Any], filters: dict[str, Any]
    ) -> T | None:
        query = (
            update(self.model)
            .filter_by(**filters)
            .values(**values)
            .returning(self.model)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
