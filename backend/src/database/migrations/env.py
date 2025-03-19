import asyncio
import logging
import time
from logging.config import fileConfig

from alembic import context
from models import Base
from settings import settings
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config  # type: ignore

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name or "backend/alembic.ini")


target_metadata = Base.metadata

logger = logging.getLogger(__name__)


def do_run_migrations(connection) -> None:  # type: ignore
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    configuration = config.get_section(config.config_ini_section) or {
        "script_location": "alembic"
    }
    configuration["sqlalchemy.url"] = f"{settings.migration.dsn}?async_fallback=true"
    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    i = 1
    for _ in range(5):
        try:
            async with connectable.connect() as connection:
                await connection.run_sync(do_run_migrations)

            await connectable.dispose()
            break
        except ConnectionRefusedError as cfe:
            i *= 2
            logger.warn(f"Exception: {cfe}")
            logger.warn(f"Database connection failed, retrying in {i}s ...")
            time.sleep(i)


asyncio.run(run_migrations_online())
