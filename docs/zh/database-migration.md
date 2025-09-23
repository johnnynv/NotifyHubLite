# 数据库迁移管理

## 🔄 概述

数据库迁移是管理数据库架构变更的重要机制。NotifyHubLite 使用 **Alembic** 作为数据库迁移工具，确保数据库架构的版本控制和安全升级。

## 🛠️ Alembic 简介

Alembic 是 SQLAlchemy 官方推荐的数据库迁移工具，提供：

- **版本控制**：每个数据库变更都有唯一的版本号
- **自动生成**：根据模型变更自动生成迁移脚本
- **双向迁移**：支持升级（upgrade）和降级（downgrade）
- **分支管理**：支持多开发分支的迁移合并

## 📁 项目结构

```
NotifyHubLite/
├── migrations/                    # Alembic 迁移目录
│   ├── versions/                 # 迁移版本文件
│   │   ├── 001_initial_tables.py
│   │   ├── 002_add_pdf_preview.py
│   │   └── 003_add_indexes.py
│   ├── env.py                   # Alembic 环境配置
│   ├── script.py.mako           # 迁移脚本模板
│   └── README
├── alembic.ini                   # Alembic 主配置文件
└── app/
    ├── models/                  # SQLAlchemy 模型
    └── database.py              # 数据库连接配置
```

## ⚙️ 配置设置

### 1. alembic.ini 配置

```ini
# alembic.ini
[alembic]
# 迁移脚本目录
script_location = migrations

# 迁移脚本模板文件
file_template = %%(year)d%%(month).2d%%(day).2d_%%(hour).2d%%(minute).2d_%%(rev)s_%%(slug)s

# 数据库连接URL (从环境变量读取)
sqlalchemy.url = 

# 日志配置
[loggers]
keys = root,sqlalchemy,alembic

[handlers] 
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

### 2. env.py 配置

```python
# migrations/env.py
import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from app.models import Base  # 导入所有模型
from app.config import settings

# Alembic Config对象
config = context.config

# 设置数据库URL
config.set_main_option("sqlalchemy.url", settings.database_url)

# 日志配置
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 目标元数据
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """离线模式运行迁移"""
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
    """在线模式运行迁移"""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

## 🚀 初始化和基本使用

### 1. 初始化 Alembic

```bash
# 在项目根目录执行
alembic init migrations

# 或者如果已经有配置，直接使用现有配置
```

### 2. 创建初始迁移

```bash
# 生成初始迁移（基于现有模型）
alembic revision --autogenerate -m "Initial tables"

# 这会在 migrations/versions/ 目录生成类似文件：
# 20250923_1430_abc123def456_initial_tables.py
```

### 3. 执行迁移

```bash
# 升级到最新版本
alembic upgrade head

# 升级到特定版本
alembic upgrade abc123def456

# 降级到上一个版本
alembic downgrade -1

# 查看当前版本
alembic current

# 查看迁移历史
alembic history
```

## 📝 迁移脚本示例

### 初始表创建

```python
# migrations/versions/001_20250923_1430_initial_tables.py
"""Initial tables

Revision ID: abc123def456
Revises: 
Create Date: 2025-09-23 14:30:00.123456

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'abc123def456'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 创建 emails 表
    op.create_table('emails',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('to_addresses', sa.Text(), nullable=False),
        sa.Column('cc_addresses', sa.Text(), nullable=True),
        sa.Column('bcc_addresses', sa.Text(), nullable=True),
        sa.Column('subject', sa.Text(), nullable=False),
        sa.Column('html_content', sa.Text(), nullable=False),
        sa.Column('attachment_ids', sa.Text(), nullable=True),
        sa.Column('status', sa.String(20), nullable=True, default='pending'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('smtp_message_id', sa.String(255), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('sent_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 创建 attachments 表
    op.create_table('attachments',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('filename', sa.String(255), nullable=False),
        sa.Column('original_filename', sa.String(255), nullable=False),
        sa.Column('file_path', sa.Text(), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('mime_type', sa.String(100), nullable=False),
        sa.Column('file_hash', sa.String(64), nullable=True),
        sa.Column('upload_type', sa.String(20), nullable=False),
        sa.Column('is_inline', sa.Boolean(), nullable=True, default=False),
        sa.Column('cid', sa.String(100), nullable=True),
        sa.Column('metadata', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('expires_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=True, default=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 创建 pdf_previews 表
    op.create_table('pdf_previews',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('pdf_attachment_id', sa.String(), nullable=False),
        sa.Column('total_pages', sa.Integer(), nullable=False),
        sa.Column('preview_pages', sa.Integer(), nullable=False),
        sa.Column('preview_image_ids', sa.Text(), nullable=False),
        sa.Column('generated_html', sa.Text(), nullable=True),
        sa.Column('processing_settings', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['pdf_attachment_id'], ['attachments.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    op.drop_table('pdf_previews')
    op.drop_table('attachments')
    op.drop_table('emails')
```

### 添加索引

```python
# migrations/versions/002_20250923_1500_add_indexes.py
"""Add database indexes

Revision ID: def456abc789
Revises: abc123def456
Create Date: 2025-09-23 15:00:00.123456

"""
from alembic import op

revision = 'def456abc789'
down_revision = 'abc123def456'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 为 emails 表添加索引
    op.create_index('idx_emails_status', 'emails', ['status'])
    op.create_index('idx_emails_created_at', 'emails', ['created_at'])
    op.create_index('idx_emails_status_created', 'emails', ['status', 'created_at'])
    
    # 为 attachments 表添加索引
    op.create_index('idx_attachments_upload_type', 'attachments', ['upload_type'])
    op.create_index('idx_attachments_created_at', 'attachments', ['created_at'])
    op.create_index('idx_attachments_expires_at', 'attachments', ['expires_at'])
    op.create_index('idx_attachments_file_hash', 'attachments', ['file_hash'])
    op.create_index('idx_attachments_is_deleted', 'attachments', ['is_deleted'])
    
    # 为 pdf_previews 表添加索引
    op.create_index('idx_pdf_previews_pdf_attachment_id', 'pdf_previews', ['pdf_attachment_id'])
    op.create_index('idx_pdf_previews_created_at', 'pdf_previews', ['created_at'])

def downgrade() -> None:
    # 删除索引
    op.drop_index('idx_pdf_previews_created_at', table_name='pdf_previews')
    op.drop_index('idx_pdf_previews_pdf_attachment_id', table_name='pdf_previews')
    op.drop_index('idx_attachments_is_deleted', table_name='attachments')
    op.drop_index('idx_attachments_file_hash', table_name='attachments')
    op.drop_index('idx_attachments_expires_at', table_name='attachments')
    op.drop_index('idx_attachments_created_at', table_name='attachments')
    op.drop_index('idx_attachments_upload_type', table_name='attachments')
    op.drop_index('idx_emails_status_created', table_name='emails')
    op.drop_index('idx_emails_created_at', table_name='emails')
    op.drop_index('idx_emails_status', table_name='emails')
```

### 添加新字段

```python
# migrations/versions/003_20250924_0900_add_user_tracking.py
"""Add user tracking fields

Revision ID: ghi789jkl012
Revises: def456abc789
Create Date: 2025-09-24 09:00:00.123456

"""
from alembic import op
import sqlalchemy as sa

revision = 'ghi789jkl012'
down_revision = 'def456abc789'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 为 emails 表添加用户跟踪字段
    op.add_column('emails', sa.Column('user_id', sa.String(255), nullable=True))
    op.add_column('emails', sa.Column('api_key_used', sa.String(100), nullable=True))
    
    # 为 attachments 表添加上传者字段
    op.add_column('attachments', sa.Column('uploaded_by', sa.String(255), nullable=True))
    
    # 添加相关索引
    op.create_index('idx_emails_user_id', 'emails', ['user_id'])

def downgrade() -> None:
    # 删除索引和字段
    op.drop_index('idx_emails_user_id', table_name='emails')
    op.drop_column('attachments', 'uploaded_by')
    op.drop_column('emails', 'api_key_used')
    op.drop_column('emails', 'user_id')
```

## 🔧 开发工作流程

### 1. 修改模型后生成迁移

```bash
# 1. 修改 app/models/ 中的模型
# 2. 生成迁移脚本
alembic revision --autogenerate -m "Add new field to User model"

# 3. 检查生成的迁移脚本
# 4. 测试迁移
alembic upgrade head

# 5. 如有问题，回滚
alembic downgrade -1
```

### 2. 手动创建迁移

```bash
# 创建空的迁移文件
alembic revision -m "Custom data migration"

# 然后手动编辑生成的文件
```

### 3. 多人协作处理冲突

```bash
# 如果多个分支都有迁移，需要合并
alembic merge -m "Merge migrations" head1 head2

# 或者使用分支标签
alembic revision --branch-label feature_a -m "Feature A migration"
```

## 📋 生产环境最佳实践

### 1. 迁移前备份

```bash
# 备份数据库
pg_dump notifyhublite > backup_$(date +%Y%m%d_%H%M%S).sql

# 执行迁移
alembic upgrade head

# 验证迁移结果
```

### 2. 分阶段迁移

```bash
# 查看待应用的迁移
alembic history --verbose

# 逐个应用迁移
alembic upgrade +1  # 应用下一个迁移
# 验证结果...
alembic upgrade +1  # 继续下一个
```

### 3. 监控和回滚策略

```bash
# 检查数据库状态
alembic current
alembic show head

# 如果有问题，立即回滚
alembic downgrade abc123def456  # 回滚到指定版本
```

### 4. CI/CD 集成

```yaml
# .github/workflows/deploy.yml
steps:
  - name: Run Database Migrations
    run: |
      # 检查迁移状态
      alembic current
      
      # 执行迁移
      alembic upgrade head
      
      # 验证迁移结果
      python scripts/verify_db_schema.py
```

## 🔍 常用命令参考

```bash
# 查看命令帮助
alembic --help

# 初始化项目
alembic init migrations

# 创建迁移
alembic revision --autogenerate -m "description"
alembic revision -m "manual migration"

# 执行迁移
alembic upgrade head         # 升级到最新
alembic upgrade +2           # 升级2个版本
alembic upgrade abc123       # 升级到指定版本

# 回滚迁移
alembic downgrade -1         # 回滚1个版本
alembic downgrade abc123     # 回滚到指定版本
alembic downgrade base       # 回滚所有

# 查看状态
alembic current              # 当前版本
alembic history              # 迁移历史
alembic show abc123          # 显示特定迁移

# 生成SQL（不执行）
alembic upgrade head --sql   # 生成升级SQL
alembic downgrade -1 --sql   # 生成降级SQL
```

## ⚠️ 注意事项

### 1. 数据安全
- **总是备份**：执行迁移前必须备份数据库
- **先测试**：在测试环境完整测试迁移流程
- **可回滚**：确保每个迁移都有对应的downgrade

### 2. 性能考虑
- **大表操作**：大表的结构变更可能很耗时
- **索引创建**：在业务低峰期创建大型索引
- **分批处理**：大量数据迁移考虑分批执行

### 3. 团队协作
- **代码审查**：迁移脚本需要仔细审查
- **命名规范**：使用描述性的迁移名称
- **文档记录**：重要变更需要详细说明

---

通过 Alembic，我们可以安全、可控地管理数据库架构的演进，确保系统在持续开发中的稳定性和可维护性。
