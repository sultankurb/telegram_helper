from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.app_setup.config import settings


async_engine = create_async_engine(url=settings.DB_URL)
async_session = async_sessionmaker(bind=async_engine, expire_on_commit=False)
