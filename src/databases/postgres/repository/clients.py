from sqlalchemy.ext.asyncio import AsyncSession

from src.databases.postgres.models.clients import ClientsORM
from src.databases.postgres.repository.base import SQLAlchemyRepository


class ClientsRepository(SQLAlchemyRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session_pool=session, model=ClientsORM)
