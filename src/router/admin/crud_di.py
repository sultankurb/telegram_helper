from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.databases.postgres.models.clients import ClientsORM


async def get_clients_di(session: AsyncSession, offset: int = 0):
    stmt = select(ClientsORM).offset(offset).limit(100)
    result = await session.execute(stmt)
    return result.scalars().all()
