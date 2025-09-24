# NotifyHubLite 部署指南

## 全新机器快速部署

### 前置要求

**系统要求:**
- Linux (Ubuntu 20.04+, CentOS 7+, RHEL 8+) 
- Python 3.9+
- Docker & Docker Compose (可选，用于数据库和SMTP)
- Git

**必需软件安装:**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3 python3-pip git curl jq

# CentOS/RHEL
sudo yum install -y python3 python3-pip git curl jq

# 安装 Docker (可选)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
# 重新登录或执行: newgrp docker
```

### 步骤1: 克隆代码

```bash
# 克隆项目
git clone <YOUR_REPO_URL> NotifyHubLite
cd NotifyHubLite
```

### 步骤2: 配置环境

```bash
# 安装Python依赖
make install

# 或手动安装
pip3 install -r requirements.txt
```

### 步骤3: 配置IP和域名

```bash
# 方法1: 使用配置脚本 (推荐)
make configure

# 方法2: 手动设置环境变量
export NOTIFYHUB_SERVER_IP=YOUR_SERVER_IP
export NOTIFYHUB_DOMAIN_SUFFIX=nip.io
export NOTIFYHUB_API_KEY=your-secure-api-key-123
```

### 步骤4: 启动服务

#### 选项A: 完整Docker部署 (推荐)
```bash
# 启动所有服务 (PostgreSQL + SMTP + API)
make docker-up

# 等待服务启动
sleep 10

# 启动API服务
make api
```

#### 选项B: 仅SMTP服务Docker + 本地API
```bash
# 仅启动SMTP服务
docker-compose up -d postfix

# 启动API服务
make api
```

#### 选项C: 完全本地部署
```bash
# 使用外部SMTP服务器，直接启动API
export NOTIFYHUB_SMTP_HOST=your-smtp-server.com
export NOTIFYHUB_SMTP_PORT=587
export NOTIFYHUB_SMTP_USERNAME=your-username
export NOTIFYHUB_SMTP_PASSWORD=your-password
export NOTIFYHUB_SMTP_USE_TLS=true

make api
```

### 步骤5: 验证部署

```bash
# 检查API健康状态
make health

# 发送测试邮件
make email-test

# 查看API文档
# 浏览器访问: http://YOUR_SERVER_IP:8000/docs
```

## 一键部署脚本

创建并运行一键部署脚本:

```bash
#!/bin/bash
# quick-deploy.sh

set -e

echo "NotifyHubLite 一键部署"
echo "===================="

# 1. 检查依赖
command -v python3 >/dev/null 2>&1 || { echo "需要安装 Python 3"; exit 1; }
command -v pip3 >/dev/null 2>&1 || { echo "需要安装 pip3"; exit 1; }

# 2. 安装Python依赖
echo "安装Python依赖..."
pip3 install -r requirements.txt

# 3. 配置IP (如果需要)
if [ -n "$1" ]; then
    echo "配置服务器IP: $1"
    sed -i "s/server_ip: str = \".*\"/server_ip: str = \"$1\"/" app/config.py
fi

# 4. 启动Docker服务 (如果Docker可用)
if command -v docker >/dev/null 2>&1; then
    echo "启动Docker SMTP服务..."
    docker-compose up -d postfix
    sleep 5
fi

# 5. 启动API服务
echo "启动API服务..."
echo "API将在 http://localhost:8000 启动"
echo "API文档: http://localhost:8000/docs"
echo "按 Ctrl+C 停止服务"

cd /home/johnnynv/Development/source_code/git/github.com/nvidia/johnnynv/NotifyHubLite
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 环境变量配置参考

创建 `.env` 文件 (可选):
```bash
# 复制示例配置
cat > .env << EOF
# 服务器配置
NOTIFYHUB_SERVER_IP=203.18.50.4
NOTIFYHUB_DOMAIN_SUFFIX=nip.io
NOTIFYHUB_API_KEY=your-secure-random-api-key

# 数据库配置 (如果使用PostgreSQL)
NOTIFYHUB_DATABASE_URL=postgresql://user:pass@localhost:5432/notifyhublite

# SMTP配置 (如果使用外部SMTP)
NOTIFYHUB_SMTP_HOST=smtp.example.com
NOTIFYHUB_SMTP_PORT=587
NOTIFYHUB_SMTP_USERNAME=your-username
NOTIFYHUB_SMTP_PASSWORD=your-password
NOTIFYHUB_SMTP_USE_TLS=true
EOF
```

## 常用命令

```bash
# 查看所有可用命令
make help

# 健康检查
make health

# 发送测试邮件
make email-test

# 查看服务状态
make status

# 停止所有服务
make docker-down

# 清理缓存
make clean

# 重新配置
make configure
```

## 故障排除

### API无法启动
```bash
# 检查端口占用
lsof -i :8000

# 检查Python依赖
pip3 list | grep fastapi

# 查看详细错误
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 邮件发送失败
```bash
# 检查SMTP服务
docker logs smtp-server

# 测试SMTP连接
telnet localhost 25

# 检查配置
python3 -c "from app.config import settings; print(settings.smtp_host, settings.smtp_port)"
```

### Docker问题
```bash
# 重启Docker服务
sudo systemctl restart docker

# 清理Docker
docker system prune -f

# 重新构建
make docker-down
make docker-up
```
