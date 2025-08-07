import os
import sys
from logging.config import fileConfig

from sqlalchemy import create_engine, pool
from alembic import context

# -------------------------------
# 1️⃣ Proje kökünü PYTHONPATH’e ekle
# -------------------------------

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# -------------------------------
# 2️⃣ Modelleri ve metadata’yı import et
# -------------------------------

from database import Base
from models import announcement_model, user_model  

target_metadata = Base.metadata

# -------------------------------
# 3️⃣ Alembic config
# -------------------------------

config = context.config
fileConfig(config.config_file_name)

# -------------------------------
# 4️⃣ Migration fonksiyonları
# -------------------------------

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    url = config.get_main_option("sqlalchemy.url")
    connectable = create_engine(url, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()

# -------------------------------
# 5️⃣ Alembic’i çalıştır
# -------------------------------

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()