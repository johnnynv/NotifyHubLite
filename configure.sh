#!/bin/bash
# NotifyHubLite Configuration Script
# Allows easy modification of server IP and domain settings

set -e

# Color codes for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}NotifyHubLite Configuration Script${NC}"
echo "=================================="
echo ""

# Get current configuration
CURRENT_IP=$(grep "server_ip:" app/config.py | cut -d'"' -f2)
CURRENT_DOMAIN=$(grep "domain_suffix:" app/config.py | cut -d'"' -f2)

echo -e "${YELLOW}Current Configuration:${NC}"
echo "  Server IP: $CURRENT_IP"
echo "  Domain Suffix: $CURRENT_DOMAIN"
echo "  Base Domain: $CURRENT_IP.$CURRENT_DOMAIN"
echo "  Mail Hostname: mail.$CURRENT_IP.$CURRENT_DOMAIN"
echo ""

# Ask for new IP
read -p "Enter new server IP (press Enter to keep current): " NEW_IP
if [ -z "$NEW_IP" ]; then
    NEW_IP=$CURRENT_IP
    echo "  → Using current IP: $NEW_IP"
else
    echo "  → New IP: $NEW_IP"
fi

# Ask for new domain suffix
read -p "Enter domain suffix (press Enter to keep '$CURRENT_DOMAIN'): " NEW_DOMAIN
if [ -z "$NEW_DOMAIN" ]; then
    NEW_DOMAIN=$CURRENT_DOMAIN
    echo "  → Using current domain: $NEW_DOMAIN"
else
    echo "  → New domain: $NEW_DOMAIN"
fi

echo ""
echo -e "${YELLOW}New Configuration:${NC}"
echo "  Server IP: $NEW_IP"
echo "  Domain Suffix: $NEW_DOMAIN"
echo "  Base Domain: $NEW_IP.$NEW_DOMAIN"
echo "  Mail Hostname: mail.$NEW_IP.$NEW_DOMAIN"
echo "  Default Email: noreply@$NEW_IP.$NEW_DOMAIN"
echo ""

# Confirm changes
read -p "Apply these changes? (y/N): " CONFIRM
if [[ ! $CONFIRM =~ ^[Yy]$ ]]; then
    echo -e "${RED}Configuration cancelled.${NC}"
    exit 0
fi

echo ""
echo -e "${BLUE}Applying configuration changes...${NC}"

# Update app/config.py
echo "  → Updating app/config.py..."
sed -i "s/server_ip: str = \".*\"/server_ip: str = \"$NEW_IP\"/" app/config.py
sed -i "s/domain_suffix: str = \".*\"/domain_suffix: str = \"$NEW_DOMAIN\"/" app/config.py

# Set environment variables for Docker
echo "  → Setting environment variables for Docker..."
export SERVER_IP="$NEW_IP"
export DOMAIN_SUFFIX="$NEW_DOMAIN"

echo ""
echo -e "${GREEN}✅ Configuration updated successfully!${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Restart the API server: ${BLUE}make api${NC}"
echo "  2. Test the configuration: ${BLUE}make email-test${NC}"
echo "  3. For Docker services: ${BLUE}SERVER_IP=$NEW_IP DOMAIN_SUFFIX=$NEW_DOMAIN make docker-up${NC}"
echo ""
echo -e "${YELLOW}Environment variables for this session:${NC}"
echo "  export SERVER_IP=\"$NEW_IP\""
echo "  export DOMAIN_SUFFIX=\"$NEW_DOMAIN\""
