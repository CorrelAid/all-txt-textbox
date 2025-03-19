from typing import AsyncGenerator

from settings import settings
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


engine = create_async_engine(
    url=settings.database.dsn,
    future=True,
    pool_pre_ping=True,
    max_overflow=0,
)
LocalAsyncSession = async_sessionmaker(bind=engine, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with LocalAsyncSession.begin() as session:
        yield session
