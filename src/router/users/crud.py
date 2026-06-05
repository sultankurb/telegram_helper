from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.databases.postgres.models.clients import ClientsORM
from src.databases.postgres import MediaRepository


async def insert_client(session: AsyncSession, data: dict):
    stmt = insert(ClientsORM).values(data)
    await session.execute(stmt)
    await session.commit()


async def select_clients(
    session: AsyncSession, offset: int = 0, limit: int = 100
):
    stmt = select(ClientsORM).offset(offset).limit(limit)
    result = await session.execute(stmt)
    return result.scalars().unique()

async def get_recent_media(session: AsyncSession, limit: int = 5):
    media_repo = MediaRepository(session=session)
    return await media_repo.select_all(limit=limit)

async def get_client_by_telegram_id(session: AsyncSession, telegram_id: int):
    stmt = select(ClientsORM).where(ClientsORM.telegram_id == telegram_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()
