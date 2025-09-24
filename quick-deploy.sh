#!/bin/bash
# NotifyHubLite 一键部署脚本
# 用法: ./quick-deploy.sh [SERVER_IP] [API_KEY]

set -e

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════╗"
echo "║        NotifyHubLite 一键部署         ║"
echo "╚═══════════════════════════════════════╝"
echo -e "${NC}"

# 获取参数
SERVER_IP=${1:-"203.18.50.4"}
API_KEY=${2:-"notify-hub-api-key-123"}

echo -e "${YELLOW}部署配置:${NC}"
echo "  服务器IP: $SERVER_IP"
echo "  API密钥: $API_KEY"
echo "  域名: $SERVER_IP.nip.io"
echo ""

# 步骤1: 检查依赖
echo -e "${BLUE}[1/6] 检查系统依赖...${NC}"
check_dependency() {
    if ! command -v $1 >/dev/null 2>&1; then
        echo -e "${RED}错误: 需要安装 $1${NC}"
        echo "请先安装: $2"
        exit 1
    else
        echo -e "${GREEN}✓${NC} $1 已安装"
    fi
}

check_dependency "python3" "sudo apt install python3 python3-pip"
check_dependency "pip3" "sudo apt install python3-pip"
check_dependency "curl" "sudo apt install curl"

# 检查可选依赖
if command -v docker >/dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Docker 已安装"
    DOCKER_AVAILABLE=true
else
    echo -e "${YELLOW}!${NC} Docker 未安装 (将使用外部SMTP)"
    DOCKER_AVAILABLE=false
fi

if command -v jq >/dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} jq 已安装"
else
    echo -e "${YELLOW}!${NC} jq 未安装 (JSON输出将不会格式化)"
fi

# 步骤2: 安装Python依赖
echo ""
echo -e "${BLUE}[2/6] 安装Python依赖...${NC}"
if [ -f "requirements.txt" ]; then
    pip3 install -r requirements.txt --user
    echo -e "${GREEN}✓${NC} Python依赖安装完成"
else
    echo -e "${RED}错误: 找不到 requirements.txt 文件${NC}"
    exit 1
fi

# 步骤3: 配置应用
echo ""
echo -e "${BLUE}[3/6] 配置应用设置...${NC}"
if [ "$SERVER_IP" != "203.18.50.4" ]; then
    echo "更新服务器IP配置..."
    sed -i "s/server_ip: str = \".*\"/server_ip: str = \"$SERVER_IP\"/" app/config.py
fi

if [ "$API_KEY" != "notify-hub-api-key-123" ]; then
    echo "更新API密钥..."
    sed -i "s/api_key: str = \".*\"/api_key: str = \"$API_KEY\"/" app/config.py
fi

echo -e "${GREEN}✓${NC} 配置更新完成"

# 步骤4: 启动SMTP服务
echo ""
echo -e "${BLUE}[4/6] 启动SMTP服务...${NC}"
if [ "$DOCKER_AVAILABLE" = true ]; then
    echo "使用Docker启动Postfix SMTP服务..."
    export SERVER_IP="$SERVER_IP"
    export DOMAIN_SUFFIX="nip.io"
    
    docker-compose up -d postfix
    echo "等待SMTP服务启动..."
    sleep 5
    
    if docker ps | grep -q smtp-server; then
        echo -e "${GREEN}✓${NC} SMTP服务启动成功"
    else
        echo -e "${RED}错误: SMTP服务启动失败${NC}"
        docker logs smtp-server
        exit 1
    fi
else
    echo -e "${YELLOW}跳过Docker SMTP服务 (需要配置外部SMTP)${NC}"
fi

# 步骤5: 验证配置
echo ""
echo -e "${BLUE}[5/6] 验证配置...${NC}"
python3 -c "
from app.config import settings
print('配置验证:')
print(f'  ✓ 服务器IP: {settings.server_ip}')
print(f'  ✓ 基础域名: {settings.base_domain}')
print(f'  ✓ 邮件主机: {settings.mail_hostname}')
print(f'  ✓ 默认发件人: {settings.default_from_email}')
print(f'  ✓ API密钥: {settings.api_key[:8]}...')
"

# 步骤6: 启动API服务
echo ""
echo -e "${BLUE}[6/6] 启动API服务...${NC}"

# 设置环境变量
export PYTHONPATH=$PWD

echo -e "${GREEN}"
echo "╔═══════════════════════════════════════╗"
echo "║           部署完成！                  ║"
echo "╚═══════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${YELLOW}访问信息:${NC}"
echo "  API服务: http://$SERVER_IP:8000"
echo "  API文档: http://$SERVER_IP:8000/docs"
echo "  健康检查: http://$SERVER_IP:8000/health"
echo ""
echo -e "${YELLOW}测试命令:${NC}"
echo "  健康检查: curl http://localhost:8000/health"
echo "  发送测试邮件: make email-test"
echo ""
echo -e "${YELLOW}停止服务:${NC}"
echo "  按 Ctrl+C 停止API服务"
if [ "$DOCKER_AVAILABLE" = true ]; then
    echo "  停止SMTP: docker-compose down"
fi
echo ""

echo -e "${BLUE}正在启动API服务...${NC}"
echo "按 Ctrl+C 停止服务"
echo ""

# 启动API服务
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
