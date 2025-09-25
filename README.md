# NotifyHubLite

🚀 Lightweight Email Notification System - Support plain text email sending, API authentication, Docker deployment

## Quick Start (Fresh Machine)

### One-Click Deployment
```bash
# Clone project
git clone <YOUR_REPO_URL> NotifyHubLite
cd NotifyHubLite

# One-click deployment (using default IP)
./quick-deploy.sh

# Or specify IP
./quick-deploy.sh 192.168.1.100

# Or use Makefile
make deploy IP=192.168.1.100
```

### Manual Deployment
```bash
# 1. Install dependencies
make install

# 2. Configure IP (optional)
make configure

# 3. Start services
make docker-up  # Start SMTP service
make api        # Start API service
```

## Verify Deployment

```bash
# Health check
make health

# Send test email
make email-test

# View API documentation
# Browser access: http://YOUR_IP:8000/docs
```

## API Usage

### Send Email
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

### API Authentication
- Default API Key: `notify-hub-api-key-123`
- Production environment: `export NOTIFYHUB_API_KEY=your-secure-key`

## More Commands

```bash
make help          # View all commands
make status         # View service status
make clean          # Clean cache
make docker-down    # Stop Docker services
```

## Documentation

- [Deployment Guide](DEPLOYMENT.md) - Detailed deployment instructions
- [Implementation Documentation](docs/zh/implementation.md) - Technical implementation details
- [API Documentation](http://localhost:8000/docs) - Online API documentation

## Tech Stack

- **Backend**: FastAPI + Python 3.9+
- **SMTP**: Postfix (Docker) + NVIDIA internal relay
- **Database**: PostgreSQL (optional)
- **Deployment**: Docker Compose
- **Domain**: nip.io (development) / Custom domain (production)