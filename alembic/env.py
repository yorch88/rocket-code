from logging.config import fileConfig
from alembic import context
from sqlalchemy import engine_from_config, pool
import os, sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.db import Base
from app import models
from app.config import get_settings

# ===== Alembic config ===== #
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


# ===== URL de conexión dinámica ===== #
def get_url():
    """
    Devuelve la URL de conexión de la base de datos.
    Prioriza la variable de entorno DATABASE_URL (útil para CI/CD).
    Si no existe, construye la URL usando get_settings().
    """
    env_url = os.getenv("DATABASE_URL")
    if env_url:
        return env_url

    s = get_settings()
    return (
        f"postgresql+psycopg2://{s.POSTGRES_USER}:{s.POSTGRES_PASSWORD}"
        f"@{s.POSTGRES_HOST}:{s.POSTGRES_PORT}/{s.POSTGRES_DB}"
    )


# ===== Modo offline ===== #
def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        compare_server_default=True
    )

    with context.begin_transaction():
        context.run_migrations()


# ===== Modo online ===== #
def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        {"sqlalchemy.url": get_url()},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


# ===== Ejecutar ===== #
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
