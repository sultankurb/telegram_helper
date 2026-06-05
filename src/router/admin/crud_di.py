import logging

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.databases.postgres import ClientsRepository, MediaRepository

logger = logging.getLogger(__name__)


async def get_clients_di(
        session: AsyncSession,
        offset: int = 0
):
    client_repo = ClientsRepository(session=session)
    return await client_repo.select_all(offset=offset)


async def add_media_di(
        session: AsyncSession,
        data: dict
):
    media_repo = MediaRepository(session=session)
    try:
        await media_repo.insert_one(data=data)
        await session.commit()
    except SQLAlchemyError as e:
        await session.rollback()
        logger.error(msg=e)