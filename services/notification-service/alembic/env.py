"""Task: T028 — Alembic async environment for Notification Service.

Targets notification_service schema in PostgreSQL via asyncpg.
"""

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine

from app.config import settings
from app.db.session import Base

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = settings.DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        version_table_schema=settings.DB_SCHEMA,
        include_schemas=True,
    )
    with context.begin_transaction():
        context.execute(f"CREATE SCHEMA IF NOT EXISTS {settings.DB_SCHEMA}")
        context.execute(f"SET search_path TO {settings.DB_SCHEMA}")
        context.run_migrations()


def do_run_migrations(connection) -> None:
    """Run migrations with the given connection."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        version_table_schema=settings.DB_SCHEMA,
        include_schemas=True,
    )
    with context.begin_transaction():
        context.execute(f"CREATE SCHEMA IF NOT EXISTS {settings.DB_SCHEMA}")
        context.execute(f"SET search_path TO {settings.DB_SCHEMA}")
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in 'online' mode with async engine."""
    connectable = create_async_engine(settings.DATABASE_URL)

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
