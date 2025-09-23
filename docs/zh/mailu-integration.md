# Mailu SMTP 服务器集成指南

## 📧 概述

本文档介绍如何使用 Mailu 邮件服务器为 NotifyHubLite 提供 SMTP 服务，实现完全自托管的邮件解决方案。

## 🏗️ Mailu 简介

**Mailu** 是一个开源的邮件服务器套件，提供：

- **SMTP/IMAP/POP3** 服务
- **Web 邮箱界面** (Roundcube/Rainloop)
- **管理界面** 用户和域名管理
- **反垃圾邮件** (Rspamd)
- **病毒扫描** (ClamAV)
- **DKIM/SPF/DMARC** 支持
- **Docker 化部署**

## 🔧 完整部署方案

### 1. Docker Compose 主配置

**docker-compose.yml:**
```yaml
version: '3.8'

networks:
  mailu:
    driver: bridge
    ipam:
      driver: default
      config:
        - subnet: 192.168.203.0/24
  notifyhub:
    driver: bridge

volumes:
  # NotifyHubLite 数据
  postgres_data:
  uploads_data:
  
  # Mailu 数据
  mailu_filter:
  mailu_dkim:
  mailu_overrides:
  mailu_data:
  mailu_mail:
  mailu_redis:

services:
  # =============================================================================
  # NotifyHubLite 服务
  # =============================================================================
  
  # 应用服务
  notifyhub-app:
    build: .
    container_name: notifyhub-app
    environment:
      - DATABASE_URL=postgresql://notifyhub:${POSTGRES_PASSWORD}@postgres:5432/notifyhublite
      - SMTP_HOST=mailu-front
      - SMTP_PORT=587
      - SMTP_USERNAME=${MAILU_SMTP_USER}
      - SMTP_PASSWORD=${MAILU_SMTP_PASSWORD}
      - SMTP_USE_TLS=true
      - API_KEY=${API_KEY}
    volumes:
      - uploads_data:/app/uploads
      - ./.env:/app/.env
    depends_on:
      - postgres
      - mailu-front
    networks:
      - notifyhub
      - mailu
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # 数据库服务
  postgres:
    image: postgres:15
    container_name: notifyhub-postgres
    environment:
      POSTGRES_DB: notifyhublite
      POSTGRES_USER: notifyhub
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - notifyhub
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U notifyhub"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Nginx 反向代理
  nginx:
    image: nginx:alpine
    container_name: notifyhub-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    depends_on:
      - notifyhub-app
    networks:
      - notifyhub
      - mailu
    restart: unless-stopped

  # =============================================================================
  # Mailu 邮件服务器
  # =============================================================================

  # Redis (Mailu 缓存)
  mailu-redis:
    image: redis:7-alpine
    container_name: mailu-redis
    restart: unless-stopped
    volumes:
      - mailu_redis:/data
    networks:
      - mailu
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 3

  # 前端 (Nginx + 证书管理)
  mailu-front:
    image: mailu/nginx:2.0
    container_name: mailu-front
    restart: unless-stopped
    env_file: mailu/mailu.env
    logging:
      driver: journald
      options:
        tag: mailu-front
    ports:
      - "25:25"      # SMTP
      - "465:465"    # SMTPS
      - "587:587"    # SMTP Submission
      - "143:143"    # IMAP
      - "993:993"    # IMAPS
      - "110:110"    # POP3
      - "995:995"    # POP3S
      - "8080:80"    # Web 管理界面
    volumes:
      - mailu_overrides:/overrides:ro
    networks:
      mailu:
        ipv4_address: 192.168.203.254
    depends_on:
      - mailu-resolver

  # DNS 解析器
  mailu-resolver:
    image: mailu/unbound:2.0
    container_name: mailu-resolver
    env_file: mailu/mailu.env
    restart: unless-stopped
    networks:
      mailu:
        ipv4_address: 192.168.203.254

  # 管理界面
  mailu-admin:
    image: mailu/admin:2.0
    container_name: mailu-admin
    restart: unless-stopped
    env_file: mailu/mailu.env
    logging:
      driver: journald
      options:
        tag: mailu-admin
    volumes:
      - mailu_data:/data
      - mailu_dkim:/dkim
    depends_on:
      - mailu-redis
    networks:
      - mailu

  # IMAP 服务器
  mailu-imap:
    image: mailu/dovecot:2.0
    container_name: mailu-imap
    restart: unless-stopped
    env_file: mailu/mailu.env
    logging:
      driver: journald
      options:
        tag: mailu-imap
    volumes:
      - mailu_mail:/mail
      - mailu_overrides:/overrides:ro
    depends_on:
      - mailu-front
    networks:
      - mailu

  # SMTP 服务器
  mailu-smtp:
    image: mailu/postfix:2.0
    container_name: mailu-smtp
    restart: unless-stopped
    env_file: mailu/mailu.env
    logging:
      driver: journald
      options:
        tag: mailu-smtp
    volumes:
      - mailu_overrides:/overrides:ro
    depends_on:
      - mailu-front
    networks:
      - mailu

  # 反垃圾邮件
  mailu-antispam:
    image: mailu/rspamd:2.0
    container_name: mailu-antispam
    restart: unless-stopped
    env_file: mailu/mailu.env
    logging:
      driver: journald
      options:
        tag: mailu-antispam
    volumes:
      - mailu_filter:/var/lib/rspamd
      - mailu_overrides:/overrides:ro
    depends_on:
      - mailu-front
    networks:
      - mailu

  # 病毒扫描 (可选)
  mailu-antivirus:
    image: mailu/clamav:2.0
    container_name: mailu-antivirus
    restart: unless-stopped
    env_file: mailu/mailu.env
    logging:
      driver: journald
      options:
        tag: mailu-antivirus
    volumes:
      - mailu_filter:/data
    networks:
      - mailu

  # Web 邮箱界面 (可选)
  mailu-webmail:
    image: mailu/roundcube:2.0
    container_name: mailu-webmail
    restart: unless-stopped
    env_file: mailu/mailu.env
    logging:
      driver: journald
      options:
        tag: mailu-webmail
    volumes:
      - mailu_overrides:/overrides:ro
    depends_on:
      - mailu-imap
    networks:
      - mailu
```

### 2. Mailu 环境配置

**mailu/mailu.env:**
```env
# =============================================================================
# Mailu 主配置
# =============================================================================

# 版本配置
VERSION=2.0

# 密钥 (使用 openssl rand -hex 16 生成)
SECRET_KEY=your-secret-key-here

# 域名配置
DOMAIN=mail.yourcompany.com
HOSTNAMES=mail.yourcompany.com
POSTMASTER=admin

# 数据库配置 (使用内置 SQLite)
DB_FLAVOR=sqlite

# 管理员账户
INITIAL_ADMIN_ACCOUNT=admin@mail.yourcompany.com
INITIAL_ADMIN_DOMAIN=mail.yourcompany.com
INITIAL_ADMIN_PW=secure-admin-password

# =============================================================================
# 网络配置
# =============================================================================

# Web 界面
WEB_ADMIN=/admin
WEB_WEBMAIL=/webmail

# 监听地址
BIND_ADDRESS4=0.0.0.0
BIND_ADDRESS6=::1

# 子网配置
SUBNET=192.168.203.0/24
SUBNET6=fd12:3456:789a:1::/64

# =============================================================================
# TLS/SSL 配置
# =============================================================================

# TLS 配置
TLS_FLAVOR=cert
CERTIFICATE_PATH=/certs
DMARC_RUA=admin@mail.yourcompany.com
DMARC_RUF=admin@mail.yourcompany.com

# =============================================================================
# 功能配置
# =============================================================================

# 反垃圾邮件
ANTISPAM=rspamd

# 病毒扫描
ANTIVIRUS=clamav

# Web 邮箱
WEBMAIL=roundcube

# 管理界面
ADMIN=true

# =============================================================================
# 邮件配置
# =============================================================================

# 邮件大小限制 (50MB)
MESSAGE_SIZE_LIMIT=52428800

# 邮件存储配额 (1GB per user)
DEFAULT_QUOTA=1073741824

# 发送限制 (每天1000封)
MESSAGE_RATELIMIT=1000/day

# =============================================================================
# 高级配置
# =============================================================================

# 欢迎邮件
WELCOME=false
WELCOME_SUBJECT=Welcome to your new email account
WELCOME_BODY=Welcome to your new email account, you can configure your mail client in a few minutes, here are the details:

# 日志级别
LOG_LEVEL=WARNING

# 压缩
COMPRESSION=
COMPRESSION_LEVEL=

# 禁用统计
DISABLE_STATISTICS=True
```

### 3. 环境变量配置

**.env (NotifyHubLite 主配置):**
```env
# =============================================================================
# NotifyHubLite 配置
# =============================================================================
API_KEY=your-very-secure-api-key
POSTGRES_PASSWORD=secure-postgres-password

# =============================================================================
# Mailu SMTP 配置
# =============================================================================
# SMTP 用户 (在 Mailu 管理界面创建)
MAILU_SMTP_USER=noreply@mail.yourcompany.com
MAILU_SMTP_PASSWORD=smtp-user-password

# =============================================================================
# 域名配置
# =============================================================================
DOMAIN=yourcompany.com
MAIL_DOMAIN=mail.yourcompany.com
```

### 4. Nginx 配置

**nginx/nginx.conf:**
```nginx
events {
    worker_connections 1024;
}

http {
    # 基础配置
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    sendfile on;
    keepalive_timeout 65;
    client_max_body_size 30M;

    # 日志格式
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    # 上游服务
    upstream notifyhub_app {
        server notifyhub-app:8000;
    }

    upstream mailu_admin {
        server mailu-front:80;
    }

    # HTTP 重定向到 HTTPS
    server {
        listen 80;
        server_name api.yourcompany.com mail.yourcompany.com;
        return 301 https://$server_name$request_uri;
    }

    # NotifyHubLite API 服务
    server {
        listen 443 ssl http2;
        server_name api.yourcompany.com;

        # SSL 配置
        ssl_certificate /etc/nginx/ssl/api.yourcompany.com.crt;
        ssl_certificate_key /etc/nginx/ssl/api.yourcompany.com.key;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;

        # API 代理
        location / {
            proxy_pass http://notifyhub_app;
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
            proxy_pass http://notifyhub_app;
            access_log off;
        }
    }

    # Mailu 管理界面
    server {
        listen 443 ssl http2;
        server_name mail.yourcompany.com;

        # SSL 配置
        ssl_certificate /etc/nginx/ssl/mail.yourcompany.com.crt;
        ssl_certificate_key /etc/nginx/ssl/mail.yourcompany.com.key;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;

        # Mailu 代理
        location / {
            proxy_pass http://mailu_admin;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

## 🚀 部署步骤

### 1. 准备域名和 DNS

```bash
# 设置 DNS 记录
# A 记录
api.yourcompany.com     → 服务器IP
mail.yourcompany.com    → 服务器IP

# MX 记录
yourcompany.com         → mail.yourcompany.com (优先级 10)

# TXT 记录 (SPF)
yourcompany.com         → "v=spf1 mx ~all"

# TXT 记录 (DMARC)
_dmarc.yourcompany.com  → "v=DMARC1; p=quarantine; rua=mailto:admin@mail.yourcompany.com"
```

### 2. 准备 SSL 证书

```bash
# 使用 Let's Encrypt (推荐)
sudo apt install certbot

# 生成证书
sudo certbot certonly --standalone -d api.yourcompany.com
sudo certbot certonly --standalone -d mail.yourcompany.com

# 复制证书到项目目录
sudo cp /etc/letsencrypt/live/api.yourcompany.com/fullchain.pem nginx/ssl/api.yourcompany.com.crt
sudo cp /etc/letsencrypt/live/api.yourcompany.com/privkey.pem nginx/ssl/api.yourcompany.com.key
sudo cp /etc/letsencrypt/live/mail.yourcompany.com/fullchain.pem nginx/ssl/mail.yourcompany.com.crt
sudo cp /etc/letsencrypt/live/mail.yourcompany.com/privkey.pem nginx/ssl/mail.yourcompany.com.key

# 设置权限
sudo chown -R $(whoami):$(whoami) nginx/ssl/
sudo chmod 600 nginx/ssl/*.key
```

### 3. 启动服务

```bash
# 1. 创建必要目录
mkdir -p mailu/{dkim,overrides}
mkdir -p nginx/ssl

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件

# 3. 生成 Mailu 密钥
echo "SECRET_KEY=$(openssl rand -hex 16)" >> mailu/mailu.env

# 4. 启动所有服务
docker-compose up -d

# 5. 查看日志
docker-compose logs -f
```

### 4. 配置 Mailu

```bash
# 1. 访问 Mailu 管理界面
https://mail.yourcompany.com/admin

# 2. 使用初始管理员账户登录
# 用户名: admin@mail.yourcompany.com
# 密码: secure-admin-password (在 mailu.env 中设置的)

# 3. 创建 SMTP 用户账户
# - 用户名: noreply@mail.yourcompany.com
# - 密码: smtp-user-password
# - 配额: 1GB
# - 启用 SMTP 发送权限
```

### 5. 测试邮件发送

```bash
# 测试 NotifyHubLite API
curl -X POST "https://api.yourcompany.com/api/v1/emails/send" \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "to": ["test@external-domain.com"],
    "subject": "Mailu 集成测试",
    "text_content": "这是通过 Mailu SMTP 服务器发送的测试邮件。",
    "html_content": "<h1>Mailu 集成测试</h1><p>这是通过 <strong>Mailu SMTP</strong> 服务器发送的测试邮件。</p>"
  }'
```

## 🔧 高级配置

### 1. DKIM 签名设置

```bash
# 生成 DKIM 密钥
docker-compose exec mailu-admin flask mailu admin dkim --domain yourcompany.com --selector default

# 获取 DKIM 公钥
docker-compose exec mailu-admin cat /dkim/yourcompany.com.default.key

# 添加 DNS TXT 记录
# default._domainkey.yourcompany.com → "v=DKIM1; k=rsa; p=<公钥内容>"
```

### 2. 监控和日志

```bash
# 查看 Mailu 组件状态
docker-compose ps

# 查看邮件队列
docker-compose exec mailu-smtp postqueue -p

# 查看发送日志
docker-compose logs mailu-smtp | grep "status=sent"

# 查看 NotifyHubLite 日志
docker-compose logs notifyhub-app
```

### 3. 备份策略

```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/backups/notifyhub-mailu"

mkdir -p $BACKUP_DIR

# 备份 PostgreSQL
docker-compose exec -T postgres pg_dump -U notifyhub notifyhublite > $BACKUP_DIR/notifyhub_db_$DATE.sql

# 备份 Mailu 数据
docker run --rm -v notifyhublite_mailu_data:/data -v $BACKUP_DIR:/backup alpine tar czf /backup/mailu_data_$DATE.tar.gz -C /data .

# 备份 DKIM 密钥
docker run --rm -v notifyhublite_mailu_dkim:/dkim -v $BACKUP_DIR:/backup alpine tar czf /backup/mailu_dkim_$DATE.tar.gz -C /dkim .

# 清理 30 天前的备份
find $BACKUP_DIR -type f -mtime +30 -delete

echo "Backup completed: $DATE"
```

## 📊 性能优化

### 1. Mailu 性能调优

```bash
# mailu/overrides/postfix.cf
# 增加并发连接
default_process_limit = 200
smtp_process_limit = 200

# 增加队列管理器进程
qmgr_message_active_limit = 40000
qmgr_message_recipient_limit = 40000
```

### 2. 监控指标

```bash
# 邮件队列大小
docker-compose exec mailu-smtp postqueue -p | tail -n1

# 内存使用
docker stats --no-stream

# 磁盘使用
docker system df
```

## 🔒 安全加固

### 1. 防火墙配置

```bash
# 只开放必要端口
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 25/tcp    # SMTP
sudo ufw allow 80/tcp    # HTTP (重定向)
sudo ufw allow 143/tcp   # IMAP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 465/tcp   # SMTPS
sudo ufw allow 587/tcp   # SMTP Submission
sudo ufw allow 993/tcp   # IMAPS
sudo ufw enable
```

### 2. 定期更新

```bash
# 更新 Mailu 镜像
docker-compose pull
docker-compose up -d

# 更新系统
sudo apt update && sudo apt upgrade -y
```

## 📝 故障排查

### 常见问题

**1. SMTP 连接失败**
```bash
# 检查容器状态
docker-compose ps

# 测试 SMTP 连接
telnet mail.yourcompany.com 587

# 查看 SMTP 日志
docker-compose logs mailu-smtp
```

**2. 邮件进入垃圾箱**
```bash
# 检查 SPF/DKIM/DMARC 配置
# 使用在线工具测试: https://mxtoolbox.com/

# 查看反垃圾邮件日志
docker-compose logs mailu-antispam
```

**3. 证书问题**
```bash
# 检查证书有效期
openssl x509 -in nginx/ssl/api.yourcompany.com.crt -text -noout

# 自动续期 Let's Encrypt
sudo crontab -e
# 添加: 0 3 * * * certbot renew --quiet
```

---

通过这个完整的 Mailu + NotifyHubLite 集成方案，你可以拥有一个完全自托管的企业级邮件解决方案，既有专业的 SMTP 服务器，又有强大的邮件发送 API！
