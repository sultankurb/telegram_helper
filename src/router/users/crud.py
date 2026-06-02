from src.databases.postgres.models.clients import ClientsORM
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select


async def insert_client(session: AsyncSession, data: dict):
    stmt = insert(ClientsORM).values(data)
    await session.execute(stmt)
    await session.commit()

async def select_clients(session: AsyncSession, offset: int = 0, limit: int = 100):
    stmt = select(ClientsORM).offset(offset).limit(limit)
    result = await session.execute(stmt)
    return result.scalars().unique()

