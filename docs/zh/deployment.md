# 部署指南

## 🚀 快速开始

NotifyHubLite 支持多种部署方式，从本地开发到生产环境都有相应的解决方案。

## 📋 系统要求

### 最低系统要求
- **操作系统**: Linux, macOS, Windows
- **Python**: 3.9+
- **内存**: 512MB+
- **磁盘**: 1GB+ (用于存储附件)
- **网络**: 访问 SMTP 服务器

### 推荐系统配置
- **CPU**: 2核+
- **内存**: 2GB+
- **磁盘**: 10GB+ SSD
- **数据库**: PostgreSQL 12+

## 🛠️ 环境准备

### 1. Python 环境

```bash
# 确认 Python 版本
python --version  # 需要 3.9+

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\\Scripts\\activate
```

### 2. PostgreSQL 数据库

**为什么需要数据库？**
- **邮件状态跟踪**：用户发送邮件后需要查询发送状态
- **附件管理**：存储上传文件的元信息和引用关系
- **PDF预览记录**：缓存PDF转换结果，提高性能
- **系统审计**：记录操作日志，便于问题排查

**PostgreSQL 安装：**

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y postgresql postgresql-contrib

# CentOS/RHEL
sudo yum install -y postgresql-server postgresql-contrib
sudo postgresql-setup initdb
sudo systemctl enable postgresql
sudo systemctl start postgresql

# macOS
brew install postgresql
brew services start postgresql

# 创建数据库和用户
sudo -u postgres psql
```

```sql
-- 在 PostgreSQL 中执行
CREATE DATABASE notifyhublite;
CREATE USER notifyhub WITH PASSWORD 'secure-password';
GRANT ALL PRIVILEGES ON DATABASE notifyhublite TO notifyhub;
\q
```

### 3. 系统依赖

**Ubuntu/Debian:**
```bash
# 安装系统依赖
sudo apt update
sudo apt install -y python3-dev python3-pip
sudo apt install -y poppler-utils  # PDF 处理
sudo apt install -y libpq-dev      # PostgreSQL 开发库
```

**CentOS/RHEL:**
```bash
# 安装系统依赖
sudo yum install -y python3-devel python3-pip
sudo yum install -y poppler-utils
```

**macOS:**
```bash
# 使用 Homebrew 安装
brew install poppler
brew install postgresql  # 可选
```

**Windows:**
```bash
# 需要手动安装 poppler
# 下载: https://github.com/oschwartz10612/poppler-windows/releases
# 解压并添加到 PATH 环境变量
```

## 📦 安装方式

### 方式一: 源码安装（推荐开发环境）

```bash
# 1. 克隆代码
git clone https://github.com/your-repo/NotifyHubLite.git
cd NotifyHubLite

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env 文件

# 4. 初始化数据库迁移
alembic init migrations

# 5. 创建初始迁移
alembic revision --autogenerate -m "Initial tables"

# 6. 执行迁移
alembic upgrade head

# 7. 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 方式二: Docker 部署（推荐生产环境）

```bash
# 1. 克隆代码
git clone https://github.com/your-repo/NotifyHubLite.git
cd NotifyHubLite

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件

# 3. 构建并启动
docker-compose up -d

# 4. 查看日志
docker-compose logs -f app
```

### 方式三: Docker Hub 镜像

```bash
# 1. 拉取镜像
docker pull notifyhublite/app:latest

# 2. 创建配置文件
mkdir -p /opt/notifyhublite
cat > /opt/notifyhublite/.env << EOF
# 基础配置
DATABASE_URL=sqlite:///./emails.db
API_KEY=your-secure-api-key

# SMTP 配置
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_USE_TLS=true

# 文件存储
UPLOAD_DIR=/app/uploads
MAX_FILE_SIZE=26214400
EOF

# 3. 运行容器
docker run -d \
  --name notifyhublite \
  -p 8000:8000 \
  -v /opt/notifyhublite/.env:/app/.env \
  -v /opt/notifyhublite/uploads:/app/uploads \
  -v /opt/notifyhublite/data:/app/data \
  notifyhublite/app:latest
```

## ⚙️ 配置说明

### 环境变量配置

创建 `.env` 文件：

```env
# =============================================================================
# 基础配置
# =============================================================================
# 应用环境: development | production
APP_ENV=production
# API Key (建议使用强密码生成器)
API_KEY=your-very-secure-api-key-here
# 服务绑定地址
HOST=0.0.0.0
PORT=8000

# =============================================================================
# 数据库配置
# =============================================================================
# PostgreSQL 数据库连接
DATABASE_URL=postgresql://notifyhub:secure-password@localhost:5432/notifyhublite

# =============================================================================
# SMTP 邮件配置
# =============================================================================
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_USE_TLS=true
SMTP_USE_SSL=false
# 发件人显示名称
SMTP_FROM_NAME=NotifyHub System

# =============================================================================
# 文件存储配置  
# =============================================================================
# 上传目录
UPLOAD_DIR=./uploads
# 文件大小限制 (字节)
MAX_FILE_SIZE=26214400        # 25MB
MAX_IMAGE_SIZE=5242880        # 5MB
MAX_PDF_SIZE=20971520         # 20MB

# =============================================================================
# PDF 处理配置
# =============================================================================
PDF_PREVIEW_PAGES_DEFAULT=3
PDF_PREVIEW_PAGES_MAX=10
PDF_PREVIEW_DPI=150

# =============================================================================
# 安全配置
# =============================================================================
# 允许的图片类型
ALLOWED_IMAGE_TYPES=image/jpeg,image/png,image/gif,image/webp
# 允许的文档类型
ALLOWED_DOCUMENT_TYPES=application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document

# =============================================================================
# 日志配置
# =============================================================================
LOG_LEVEL=INFO
LOG_FILE=./logs/app.log
```

### SMTP 服务器配置示例

**Gmail:**
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password  # 使用应用专用密码
SMTP_USE_TLS=true
```

**Outlook/Hotmail:**
```env
SMTP_HOST=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USERNAME=your-email@outlook.com
SMTP_PASSWORD=your-password
SMTP_USE_TLS=true
```

**企业邮箱 (QQ企业邮箱):**
```env
SMTP_HOST=smtp.exmail.qq.com
SMTP_PORT=465
SMTP_USERNAME=your-email@yourcompany.com
SMTP_PASSWORD=your-password
SMTP_USE_SSL=true
```

**自定义 SMTP:**
```env
SMTP_HOST=mail.yourcompany.com
SMTP_PORT=587
SMTP_USERNAME=noreply@yourcompany.com
SMTP_PASSWORD=secure-password
SMTP_USE_TLS=true
```

## 🐳 Docker 部署

### 单容器部署

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# 创建工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY app/ ./app/
COPY .env.example .env

# 创建必要目录
RUN mkdir -p uploads/images uploads/attachments uploads/pdfs uploads/temp data logs

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose 部署

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://notifyhub:password@db:5432/notifyhublite
    volumes:
      - ./uploads:/app/uploads
      - ./data:/app/data
      - ./logs:/app/logs
      - ./.env:/app/.env
    depends_on:
      - db
      - redis
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: notifyhublite
      POSTGRES_USER: notifyhub
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U notifyhub"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - app
    restart: unless-stopped

volumes:
  postgres_data:
```

### Nginx 配置

**nginx.conf:**
```nginx
events {
    worker_connections 1024;
}

http {
    upstream app_servers {
        server app:8000;
    }

    # 文件上传大小限制
    client_max_body_size 30M;
    
    server {
        listen 80;
        server_name your-domain.com;
        
        # HTTP 重定向到 HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name your-domain.com;

        # SSL 配置
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;

        # 代理到应用
        location / {
            proxy_pass http://app_servers;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # 超时设置
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }
        
        # 健康检查
        location /health {
            proxy_pass http://app_servers;
            access_log off;
        }
        
        # API 文档
        location /docs {
            proxy_pass http://app_servers;
        }
    }
}
```

## 🗄️ 数据库部署

### PostgreSQL 配置

```bash
# 1. 安装 PostgreSQL
sudo apt install postgresql postgresql-contrib

# 2. 创建数据库和用户
sudo -u postgres psql
```

```sql
-- 创建数据库
CREATE DATABASE notifyhublite;

-- 创建用户
CREATE USER notifyhub WITH PASSWORD 'secure-password';

-- 授权
GRANT ALL PRIVILEGES ON DATABASE notifyhublite TO notifyhub;

-- 退出
\q
```

```bash
# 3. 配置连接
DATABASE_URL=postgresql://notifyhub:secure-password@localhost:5432/notifyhublite

# 4. 初始化表结构
python -c "
from app.database import Base, engine
Base.metadata.create_all(bind=engine)
print('数据库初始化完成')
"
```

## 🔧 生产环境优化

### 1. 性能优化

**Gunicorn 部署:**
```bash
# 安装 Gunicorn
pip install gunicorn

# 启动多进程服务
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --max-requests 1000 \
  --max-requests-jitter 100 \
  --timeout 60 \
  --keep-alive 5
```

**systemd 服务配置:**
```ini
# /etc/systemd/system/notifyhublite.service
[Unit]
Description=NotifyHubLite API Service
After=network.target

[Service]
Type=exec
User=notifyhub
Group=notifyhub
WorkingDirectory=/opt/notifyhublite
Environment=PATH=/opt/notifyhublite/venv/bin
ExecStart=/opt/notifyhublite/venv/bin/gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
# 启用服务
sudo systemctl enable notifyhublite
sudo systemctl start notifyhublite
sudo systemctl status notifyhublite
```

### 2. 安全加固

**文件权限:**
```bash
# 创建专用用户
sudo useradd -r -s /bin/false notifyhub

# 设置目录权限
sudo chown -R notifyhub:notifyhub /opt/notifyhublite
sudo chmod 750 /opt/notifyhublite
sudo chmod 640 /opt/notifyhublite/.env
```

**防火墙配置:**
```bash
# UFW 配置
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### 3. 监控和日志

**日志轮转配置:**
```bash
# /etc/logrotate.d/notifyhublite
/opt/notifyhublite/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    notifempty
    create 0644 notifyhub notifyhub
    postrotate
        systemctl reload notifyhublite
    endscript
}
```

**监控脚本:**
```bash
#!/bin/bash
# /opt/notifyhublite/scripts/health_check.sh

# 检查服务状态
if ! curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "NotifyHubLite health check failed"
    systemctl restart notifyhublite
    
    # 发送告警邮件
    echo "NotifyHubLite service restarted at $(date)" | \
        mail -s "Service Alert" admin@yourcompany.com
fi
```

### 4. 备份策略

**数据备份脚本:**
```bash
#!/bin/bash
# /opt/notifyhublite/scripts/backup.sh

BACKUP_DIR="/opt/backups/notifyhublite"
DATE=$(date +%Y%m%d_%H%M%S)

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份数据库
pg_dump notifyhublite > $BACKUP_DIR/db_$DATE.sql

# 备份上传文件
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz -C /opt/notifyhublite uploads

# 保留30天的备份
find $BACKUP_DIR -type f -mtime +30 -delete

echo "Backup completed: $DATE"
```

**定时备份:**
```bash
# 添加到 crontab
crontab -e

# 每天凌晨2点备份
0 2 * * * /opt/notifyhublite/scripts/backup.sh >> /var/log/notifyhublite-backup.log 2>&1
```

## 🔍 故障排查

### 常见问题

**1. SMTP 连接失败**
```bash
# 检查网络连接
telnet smtp.gmail.com 587

# 检查认证信息
python -c "
import smtplib
smtp = smtplib.SMTP('smtp.gmail.com', 587)
smtp.starttls()
smtp.login('your-email@gmail.com', 'your-password')
print('SMTP 连接成功')
"
```

**2. 文件上传失败**
```bash
# 检查目录权限
ls -la uploads/
# 确保应用有读写权限

# 检查磁盘空间
df -h
```

**3. PDF 处理失败**
```bash
# 检查 poppler 安装
which pdftoppm
# 应该返回路径，如 /usr/bin/pdftoppm

# 测试 PDF 转换
python -c "
from pdf2image import convert_from_path
images = convert_from_path('test.pdf', first_page=1, last_page=1)
print(f'PDF 转换成功，生成 {len(images)} 张图片')
"
```

### 日志分析

**查看应用日志:**
```bash
# systemd 服务日志
sudo journalctl -u notifyhublite -f

# 应用日志文件
tail -f /opt/notifyhublite/logs/app.log

# Docker 日志
docker-compose logs -f app
```

**性能监控:**
```bash
# 查看资源使用
htop
iotop
netstat -tuln

# 数据库连接
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity WHERE datname='notifyhublite';"
```

## 📈 扩展部署

### 负载均衡

当单实例无法满足需求时，可以部署多个实例：

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  app1:
    build: .
    environment:
      - INSTANCE_ID=app1
    volumes:
      - shared_uploads:/app/uploads
    
  app2:
    build: .
    environment:
      - INSTANCE_ID=app2
    volumes:
      - shared_uploads:/app/uploads

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx-lb.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - app1
      - app2

volumes:
  shared_uploads:
    driver: local
```

### 云部署

**AWS ECS 部署示例:**
```json
{
  "family": "notifyhublite",
  "taskRoleArn": "arn:aws:iam::account:role/ecsTaskRole",
  "containerDefinitions": [
    {
      "name": "app",
      "image": "notifyhublite/app:latest",
      "memory": 1024,
      "cpu": 512,
      "essential": true,
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DATABASE_URL",
          "value": "postgresql://user:pass@rds-endpoint:5432/db"
        }
      ]
    }
  ]
}
```

---

这个部署指南涵盖了从开发环境到生产环境的完整部署流程，确保系统的稳定性和可维护性。
