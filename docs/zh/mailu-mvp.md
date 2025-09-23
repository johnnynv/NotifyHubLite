# Mailu MVP 快速部署指南

## 🎯 MVP目标

快速搭建一个**能正常发送邮件、不进垃圾箱**的最小可用系统。

## ⚡ 快速开始（15分钟）

### 1. 准备工作

**域名和DNS（必须先完成）：**
```bash
# 假设你的域名是 example.com
# 邮件服务器域名 mail.example.com

# 添加以下DNS记录：
mail.example.com        A     你的服务器IP
example.com            MX 10  mail.example.com  
example.com            TXT    "v=spf1 mx ~all"
```

### 2. 最简Docker Compose

**docker-compose.yml:**
```yaml
version: '3.8'

networks:
  mailu:
    driver: bridge

volumes:
  mailu_data:
  mailu_mail:
  mailu_dkim:
  postgres_data:
  uploads_data:

services:
  # =============================================================================
  # NotifyHubLite
  # =============================================================================
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://notifyhub:password123@postgres:5432/notifyhublite
      - SMTP_HOST=front
      - SMTP_PORT=587
      - SMTP_USERNAME=noreply@example.com
      - SMTP_PASSWORD=noreply123
      - SMTP_USE_TLS=true
      - API_KEY=your-api-key-123
    volumes:
      - uploads_data:/app/uploads
    depends_on:
      - postgres
      - front
    networks:
      - mailu

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: notifyhublite
      POSTGRES_USER: notifyhub
      POSTGRES_PASSWORD: password123
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - mailu

  # =============================================================================  
  # Mailu (最简配置)
  # =============================================================================
  redis:
    image: redis:7-alpine
    restart: unless-stopped
    volumes:
      - redis:/data
    networks:
      - mailu

  front:
    image: mailu/nginx:2.0
    restart: unless-stopped
    env_file: mailu.env
    ports:
      - "25:25"
      - "587:587"
      - "8080:80"    # 管理界面
    networks:
      - mailu

  admin:
    image: mailu/admin:2.0
    restart: unless-stopped
    env_file: mailu.env
    volumes:
      - mailu_data:/data
      - mailu_dkim:/dkim
    depends_on:
      - redis
    networks:
      - mailu

  imap:
    image: mailu/dovecot:2.0
    restart: unless-stopped
    env_file: mailu.env
    volumes:
      - mailu_mail:/mail
    depends_on:
      - front
    networks:
      - mailu

  smtp:
    image: mailu/postfix:2.0
    restart: unless-stopped
    env_file: mailu.env
    depends_on:
      - front
    networks:
      - mailu

  antispam:
    image: mailu/rspamd:2.0
    restart: unless-stopped
    env_file: mailu.env
    depends_on:
      - front
    networks:
      - mailu
```

### 3. 最简Mailu配置

**mailu.env:**
```env
# 基础配置
VERSION=2.0
SECRET_KEY=change-me-to-random-string
DOMAIN=example.com
HOSTNAMES=mail.example.com
POSTMASTER=admin

# 管理员 (重要！)
INITIAL_ADMIN_ACCOUNT=admin@example.com
INITIAL_ADMIN_DOMAIN=example.com  
INITIAL_ADMIN_PW=admin123

# 数据库
DB_FLAVOR=sqlite

# 网络
SUBNET=192.168.203.0/24

# 功能 (MVP最简)
ANTISPAM=rspamd
WEBMAIL=none
ADMIN=true

# TLS (MVP用自签名证书)
TLS_FLAVOR=mail

# 限制
MESSAGE_SIZE_LIMIT=52428800
```

### 4. 启动系统

```bash
# 1. 创建配置文件
cat > mailu.env << 'EOF'
# 复制上面的配置内容
EOF

# 2. 启动所有服务
docker-compose up -d

# 3. 等待启动完成 (约2-3分钟)
docker-compose logs -f

# 4. 检查服务状态
docker-compose ps
```

### 5. 配置DKIM (1分钟)

```bash
# 等Mailu完全启动后执行
sleep 120

# 生成DKIM密钥
docker-compose exec admin flask mailu admin dkim --domain example.com --selector default

# 获取公钥 (复制输出内容)
docker-compose exec admin cat /dkim/example.com.default.key
```

**添加DNS记录：**
```bash
# 将上面命令的输出添加为DNS TXT记录
default._domainkey.example.com TXT "v=DKIM1; k=rsa; p=MIGfMA0GCSqGSIb3DQEBA..."
```

### 6. 创建发送账户

```bash
# 访问管理界面
http://你的服务器IP:8080/admin

# 登录信息：
# 用户名: admin@example.com  
# 密码: admin123

# 在管理界面中：
# 1. 添加域名: example.com
# 2. 添加用户: noreply@example.com (密码: noreply123)
```

### 7. 测试发送

```bash
# 测试NotifyHubLite API
curl -X POST "http://你的服务器IP:8000/api/v1/emails/send" \
  -H "X-API-Key: your-api-key-123" \
  -H "Content-Type: application/json" \
  -d '{
    "to": ["your-email@gmail.com"],
    "subject": "MVP测试邮件",
    "text_content": "这是通过Mailu发送的测试邮件！"
  }'
```

## 🔍 故障排查

### 问题1: 邮件进垃圾箱

**检查清单：**
```bash
# 1. 验证SPF记录
dig TXT example.com | grep spf

# 2. 验证DKIM记录  
dig TXT default._domainkey.example.com

# 3. 检查发件人域名
# 确保from地址是 @example.com
```

### 问题2: 发送失败

**查看日志：**
```bash
# SMTP日志
docker-compose logs smtp

# NotifyHubLite日志
docker-compose logs app

# 管理员日志
docker-compose logs admin
```

### 问题3: 连接问题

**检查端口：**
```bash
# 检查SMTP端口
telnet 你的服务器IP 587

# 检查管理界面
curl http://你的服务器IP:8080
```

## 📈 MVP验收标准

### ✅ 成功标准
1. **能发送邮件** - API调用成功
2. **不进垃圾箱** - 邮件到达收件箱
3. **管理界面可访问** - 能创建用户
4. **DKIM验证通过** - 在线工具验证OK

### 🔧 验证方法

**1. 发送测试：**
```bash
# 发送到你的个人邮箱
curl -X POST "http://IP:8000/api/v1/emails/send" \
  -H "X-API-Key: your-api-key-123" \
  -H "Content-Type: application/json" \
  -d '{
    "to": ["你的个人邮箱"],
    "subject": "Mailu MVP 测试",
    "text_content": "如果收到这封邮件，说明Mailu配置成功！"
  }'
```

**2. 在线验证：**
- SPF: https://mxtoolbox.com/spf.aspx?domain=example.com
- DKIM: https://mxtoolbox.com/dkim.aspx?domain=example.com&selector=default

## 💡 MVP后的优化方向

### 🔒 安全加固
1. **更换默认密码**
2. **配置防火墙**
3. **SSL证书** (Let's Encrypt)

### 📊 监控
1. **邮件发送统计**
2. **错误率监控**
3. **磁盘空间监控**

### ⚡ 性能优化
1. **邮件队列优化**
2. **数据库调优**
3. **缓存配置**

---

这个MVP配置可以在15分钟内完成部署，满足基本的邮件发送需求。DKIM会自动处理，你只需要添加一条DNS记录即可！
