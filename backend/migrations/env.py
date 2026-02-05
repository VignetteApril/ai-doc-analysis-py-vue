import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# ----------------- 关键修改开始 -----------------
# 1. 将项目根目录添加到系统路径，确保能够导入 app 模块
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))

# 2. 导入你的 Base 和模型
# 必须导入所有模型类（如 User），否则 Alembic 无法检测到表的变化
from app.db.database import Base, SQLALCHEMY_DATABASE_URL
from app.models.user import User
from app.models.document import Document  # 必须导入！

# 3. 设置目标元数据
target_metadata = Base.metadata
# ----------------- 关键修改结束 -----------------

config = context.config

# ----------------- 动态设置数据库 URL -----------------
# 优先从我们的 database.py 逻辑中获取连接字符串
config.set_main_option("sqlalchemy.url", SQLALCHEMY_DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def run_migrations_offline() -> None:
    """在 '离线' 模式下运行迁移。"""
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
    """在 '在线' 模式下运行迁移。"""
    # 这一步会使用我们刚才 set_main_option 注入的 URL
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # 开启此项可以让 Alembic 检测字段类型变化、长度变化等细节
            compare_type=True
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()