# NotifyHubLite

🚀 轻量级邮件通知系统 - 支持纯文本邮件发送、API认证、Docker部署

## 快速开始 (全新机器)

### 一键部署
```bash
# 克隆项目
git clone <YOUR_REPO_URL> NotifyHubLite
cd NotifyHubLite

# 一键部署 (使用默认IP)
./quick-deploy.sh

# 或指定IP
./quick-deploy.sh 192.168.1.100

# 或使用Makefile
make deploy IP=192.168.1.100
```

### 手动部署
```bash
# 1. 安装依赖
make install

# 2. 配置IP (可选)
make configure

# 3. 启动服务
make docker-up  # 启动SMTP服务
make api        # 启动API服务
```

## 验证部署

```bash
# 健康检查
make health

# 发送测试邮件
make email-test

# 查看API文档
# 浏览器访问: http://YOUR_IP:8000/docs
```

## API使用

### 发送邮件
```bash
curl -X POST "http://localhost:8000/api/v1/emails/send-plain" \
  -H "Authorization: Bearer notify-hub-api-key-123" \
  -H "Content-Type: application/json" \
  -d '{
    "recipients": ["user@example.com"],
    "subject": "Hello from NotifyHubLite",
    "body": "This is a test email."
  }'
```

### API认证
- 默认API Key: `notify-hub-api-key-123`
- 生产环境请修改: `export NOTIFYHUB_API_KEY=your-secure-key`

## 更多命令

```bash
make help          # 查看所有命令
make status         # 查看服务状态
make clean          # 清理缓存
make docker-down    # 停止Docker服务
```

## 文档

- [部署指南](DEPLOYMENT.md) - 详细部署说明
- [实现文档](docs/zh/implementation.md) - 技术实现细节
- [API文档](http://localhost:8000/docs) - 在线API文档

## 技术栈

- **后端**: FastAPI + Python 3.9+
- **SMTP**: Postfix (Docker) + NVIDIA内网中继
- **数据库**: PostgreSQL (可选)
- **部署**: Docker Compose
- **域名**: nip.io (开发) / 自定义域名 (生产)
