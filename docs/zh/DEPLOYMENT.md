# NotifyHubLite Deployment Guide

## Quick Deployment for Fresh Machine

### Prerequisites

**System Requirements:**
- Linux (Ubuntu 20.04+, CentOS 7+, RHEL 8+) 
- Python 3.9+
- Docker & Docker Compose (optional, for database and SMTP)
- Git

**Required Software Installation:**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3 python3-pip git curl jq

# CentOS/RHEL
sudo yum install -y python3 python3-pip git curl jq

# Install Docker (optional)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
# Re-login or execute: newgrp docker
```

### Step 1: Clone Code

```bash
# Clone project
git clone <YOUR_REPO_URL> NotifyHubLite
cd NotifyHubLite
```

### Step 2: Configure Environment

```bash
# Install Python dependencies
make install

# Or install manually
pip3 install -r requirements.txt
```

### Step 3: Configure IP and Domain

```bash
# Method 1: Use configuration script (recommended)
make configure

# Method 2: Set environment variables manually
export NOTIFYHUB_SERVER_IP=YOUR_SERVER_IP
export NOTIFYHUB_DOMAIN_SUFFIX=nip.io
export NOTIFYHUB_API_KEY=your-secure-api-key-123
```

### Step 4: Start Services

#### Option A: Full Docker Deployment (Recommended)
```bash
# Start all services (PostgreSQL + SMTP + API)
make docker-up

# Wait for services to start
sleep 10

# Start API service
make api
```

#### Option B: SMTP Service Docker + Local API
```bash
# Start SMTP service only
docker-compose up -d postfix

# Start API service
make api
```

#### Option C: Complete Local Deployment
```bash
# Use external SMTP server, start API directly
export NOTIFYHUB_SMTP_HOST=your-smtp-server.com
export NOTIFYHUB_SMTP_PORT=587
export NOTIFYHUB_SMTP_USERNAME=your-username
export NOTIFYHUB_SMTP_PASSWORD=your-password
export NOTIFYHUB_SMTP_USE_TLS=true

make api
```

### Step 5: Verify Deployment

```bash
# Check API health status
make health

# Send test email
make email-test

# View API documentation
# Browser access: http://YOUR_SERVER_IP:8000/docs
```

## One-Click Deployment Script

Create and run one-click deployment script:

```bash
#!/bin/bash
# quick-deploy.sh

set -e

echo "NotifyHubLite One-Click Deployment"
echo "=================================="

# 1. Check dependencies
command -v python3 >/dev/null 2>&1 || { echo "Python 3 installation required"; exit 1; }
command -v pip3 >/dev/null 2>&1 || { echo "pip3 installation required"; exit 1; }

# 2. Install Python dependencies
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

# 3. Configure IP (if needed)
if [ -n "$1" ]; then
    echo "Configuring server IP: $1"
    sed -i "s/server_ip: str = \".*\"/server_ip: str = \"$1\"/" app/config.py
fi

# 4. Start Docker service (if Docker available)
if command -v docker >/dev/null 2>&1; then
    echo "Starting Docker SMTP service..."
    docker-compose up -d postfix
    sleep 5
fi

# 5. Start API service
echo "Starting API service..."
echo "API will start at http://localhost:8000"
echo "API documentation: http://localhost:8000/docs"
echo "Press Ctrl+C to stop service"

cd /home/johnnynv/Development/source_code/git/github.com/nvidia/johnnynv/NotifyHubLite
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Environment Variables Configuration Reference

Create `.env` file (optional):
```bash
# Copy example configuration
cat > .env << EOF
# Server configuration
NOTIFYHUB_SERVER_IP=203.18.50.4
NOTIFYHUB_DOMAIN_SUFFIX=nip.io
NOTIFYHUB_API_KEY=your-secure-random-api-key

# Database configuration (if using PostgreSQL)
NOTIFYHUB_DATABASE_URL=postgresql://user:pass@localhost:5432/notifyhublite

# SMTP configuration (if using external SMTP)
NOTIFYHUB_SMTP_HOST=smtp.example.com
NOTIFYHUB_SMTP_PORT=587
NOTIFYHUB_SMTP_USERNAME=your-username
NOTIFYHUB_SMTP_PASSWORD=your-password
NOTIFYHUB_SMTP_USE_TLS=true
EOF
```

## Common Commands

```bash
# View all available commands
make help

# Health check
make health

# Send test email
make email-test

# View service status
make status

# Stop all services
make docker-down

# Clean cache
make clean

# Reconfigure
make configure
```

## Troubleshooting

### API Cannot Start
```bash
# Check port usage
lsof -i :8000

# Check Python dependencies
pip3 list | grep fastapi

# View detailed errors
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Email Sending Failed
```bash
# Check SMTP service
docker logs smtp-server

# Test SMTP connection
telnet localhost 25

# Check configuration
python3 -c "from app.config import settings; print(settings.smtp_host, settings.smtp_port)"
```

### Docker Issues
```bash
# Restart Docker service
sudo systemctl restart docker

# Clean Docker
docker system prune -f

# Rebuild
make docker-down
make docker-up
```