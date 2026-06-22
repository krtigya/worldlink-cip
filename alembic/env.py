"""Alembic migration environment."""
from logging.config import fileConfig
import os
from sqlalchemy import engine_from_config, pool
from alembic import context
from app.models.base import Base
from app.models import *  # noqa: F401,F403 — ensure all models are imported


config  = context.config
fileConfig(config.config_file_name)
target_metadata = Base.metadata
import os


def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata,
                      literal_binds=True, dialect_opts={"paramstyle": "named"})
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    # 1. Get the configuration dictionary from alembic.ini
    alembic_config = config.get_section(config.config_ini_section) or {}
    
    # 2. If DATABASE_URL_SYNC exists in the environment, override the ini file
    env_url = os.getenv("DATABASE_URL_SYNC")
    if env_url:
        alembic_config["sqlalchemy.url"] = env_url

    # 3. Create the engine with the updated configuration
    connectable = engine_from_config(
        alembic_config,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
