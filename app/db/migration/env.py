from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# Import Base (metadata)
from app.models.user_model import User  # pastikan semua model ter-import
from sqlmodel import SQLModel

# Alembic config
config = context.config

# Load config file
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# TARGET METADATA
# SQLModel => pakai metadata = SQLModel.metadata
target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")

    # UBAH URL ASYNC → SYNC
    if "+asyncpg" in url:
        url = url.replace("+asyncpg", "")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    cfg = config.get_section(config.config_ini_section)

    # UBAH URL ASYNC → SYNC
    if "+asyncpg" in cfg["sqlalchemy.url"]:
        cfg["sqlalchemy.url"] = cfg["sqlalchemy.url"].replace("+asyncpg", "")

    connectable = engine_from_config(
        cfg,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
