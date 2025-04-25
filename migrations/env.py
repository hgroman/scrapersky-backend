import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Add the project's src directory to the Python path
# This allows Alembic to find your models
current_path = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_path, "..")  # Assuming env.py is in migrations/
sys.path.insert(0, project_root)

# --- Import Base and Models ---
# Import the Base object from where it's defined

# Import all your model modules here so Alembic autogenerate can see them
# Add any other models that inherit from Base
# If models for other tables (roles, permissions, tasks, features, etc.) exist, import them too.
# Example: import src.models.role
# Example: import src.models.permission
# --- Import db_config for direct sync connection string --- #
from src.db.engine import db_config
from src.models.base import Base

# ------------------------------------------------------------ #

# Set the target metadata
target_metadata = Base.metadata
# -----------------------------


# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    Uses the DIRECT synchronous connection string from db_config
    to avoid issues with Supavisor pooling during DDL operations.
    """
    # Get the direct synchronous connection string
    sync_url = db_config.sync_connection_string
    if not sync_url:
        raise ValueError(
            "Direct synchronous database URL (sync_connection_string) is not configured."
        )

    # Create a synchronous engine using the direct URL
    connectable = create_engine(sync_url, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
