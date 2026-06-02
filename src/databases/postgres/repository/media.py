from sqlalchemy.ext.asyncio import AsyncSession

from src.databases.postgres.models.media import MediaORM
from src.databases.postgres.repository.base import SQLAlchemyRepository


class MediaRepository(SQLAlchemyRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session_pool=session, model=MediaORM)
