#!/bin/bash
# NotifyHubLite One-Click Deployment Script
# Usage: ./quick-deploy.sh [SERVER_IP] [API_KEY]

set -e

# Color definitions
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════╗"
echo "║        NotifyHubLite One-Click        ║"
echo "║           Deployment                  ║"
echo "╚═══════════════════════════════════════╝"
echo -e "${NC}"

# Get parameters
SERVER_IP=${1:-"203.18.50.4"}
API_KEY=${2:-"notify-hub-api-key-123"}

echo -e "${YELLOW}Deployment Configuration:${NC}"
echo "  Server IP: $SERVER_IP"
echo "  API Key: $API_KEY"
echo "  Domain: $SERVER_IP.nip.io"
echo ""

# Step 1: Check dependencies
echo -e "${BLUE}[1/6] Checking system dependencies...${NC}"
check_dependency() {
    if ! command -v $1 >/dev/null 2>&1; then
        echo -e "${RED}Error: $1 installation required${NC}"
        echo "Please install first: $2"
        exit 1
    else
        echo -e "${GREEN}✓${NC} $1 installed"
    fi
}

check_dependency "python3" "sudo apt install python3 python3-pip"
check_dependency "pip3" "sudo apt install python3-pip"
check_dependency "curl" "sudo apt install curl"

# Check optional dependencies
if command -v docker >/dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Docker installed"
    DOCKER_AVAILABLE=true
else
    echo -e "${YELLOW}!${NC} Docker not installed (will use external SMTP)"
    DOCKER_AVAILABLE=false
fi

if command -v jq >/dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} jq installed"
else
    echo -e "${YELLOW}!${NC} jq not installed (JSON output will not be formatted)"
fi

# Step 2: Install Python dependencies
echo ""
echo -e "${BLUE}[2/6] Installing Python dependencies...${NC}"
if [ -f "requirements.txt" ]; then
    pip3 install -r requirements.txt --user
    echo -e "${GREEN}✓${NC} Python dependencies installation completed"
else
    echo -e "${RED}Error: requirements.txt file not found${NC}"
    exit 1
fi

# Step 3: Configure application
echo ""
echo -e "${BLUE}[3/6] Configuring application settings...${NC}"
if [ "$SERVER_IP" != "203.18.50.4" ]; then
    echo "Updating server IP configuration..."
    sed -i "s/server_ip: str = \".*\"/server_ip: str = \"$SERVER_IP\"/" app/config.py
fi

if [ "$API_KEY" != "notify-hub-api-key-123" ]; then
    echo "Updating API key..."
    sed -i "s/api_key: str = \".*\"/api_key: str = \"$API_KEY\"/" app/config.py
fi

echo -e "${GREEN}✓${NC} Configuration update completed"

# Step 4: Start SMTP service
echo ""
echo -e "${BLUE}[4/6] Starting SMTP service...${NC}"
if [ "$DOCKER_AVAILABLE" = true ]; then
    echo "Starting Postfix SMTP service using Docker..."
    export SERVER_IP="$SERVER_IP"
    export DOMAIN_SUFFIX="nip.io"
    
    sudo docker compose up -d postfix
    echo "Waiting for SMTP service to start..."
    sleep 5
    
    if sudo docker ps | grep -q smtp-server; then
        echo -e "${GREEN}✓${NC} SMTP service started successfully"
    else
        echo -e "${RED}Error: SMTP service failed to start${NC}"
        sudo docker logs smtp-server
        exit 1
    fi
else
    echo -e "${YELLOW}Skipping Docker SMTP service (external SMTP configuration required)${NC}"
fi

# Step 5: Verify configuration
echo ""
echo -e "${BLUE}[5/6] Verifying configuration...${NC}"
python3 -c "
from app.config import settings
print('Configuration verification:')
print(f'  ✓ Server IP: {settings.server_ip}')
print(f'  ✓ Base domain: {settings.base_domain}')
print(f'  ✓ Mail hostname: {settings.mail_hostname}')
print(f'  ✓ Default sender: {settings.default_from_email}')
print(f'  ✓ API key: {settings.api_key[:8]}...')
"

# Step 6: Start API service
echo ""
echo -e "${BLUE}[6/6] Starting API service...${NC}"

# Set environment variables
export PYTHONPATH=$PWD

echo -e "${GREEN}"
echo "╔═══════════════════════════════════════╗"
echo "║           Deployment Complete!        ║"
echo "╚═══════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${YELLOW}Access Information:${NC}"
echo "  API Service: http://$SERVER_IP:8000"
echo "  API Documentation: http://$SERVER_IP:8000/docs"
echo "  Health Check: http://$SERVER_IP:8000/health"
echo ""
echo -e "${YELLOW}Test Commands:${NC}"
echo "  Health check: curl http://localhost:8000/health"
echo "  Send test email: make email-test"
echo ""
echo -e "${YELLOW}Stop Services:${NC}"
echo "  Press Ctrl+C to stop API service"
if [ "$DOCKER_AVAILABLE" = true ]; then
    echo "  Stop SMTP: sudo docker compose down"
fi
echo ""

echo -e "${BLUE}Starting API service...${NC}"
echo "Press Ctrl+C to stop service"
echo ""

# Start API service
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload