# NotifyHubLite Makefile
# Usage: make <target>

.PHONY: help install dev test clean docker-up docker-down api docs lint format check

# Default target
help:
	@echo "NotifyHubLite Development Commands"
	@echo "=================================="
	@echo ""
	@echo "Setup & Installation:"
	@echo "  install     Install Python dependencies"
	@echo "  dev         Install development dependencies"
	@echo ""
	@echo "Development:"
	@echo "  api         Start FastAPI development server"
	@echo "  docs        Open API documentation in browser"
	@echo "  test        Run tests"
	@echo "  lint        Run linting checks"
	@echo "  format      Format code with black"
	@echo "  check       Run all checks (lint + format + test)"
	@echo ""
	@echo "Docker:"
	@echo "  docker-up   Start all services (PostgreSQL + SMTP)"
	@echo "  docker-down Stop all services"
	@echo "  docker-logs View service logs"
	@echo ""
	@echo "Utilities:"
	@echo "  clean       Clean cache and temporary files"
	@echo "  db-init     Initialize database"
	@echo "  email-test  Send test email"
	@echo ""

# Python & Dependencies
install:
	@echo "Installing Python dependencies..."
	pip install -r requirements.txt

dev:
	@echo "Installing development dependencies..."
	pip install -r requirements.txt
	pip install black flake8 pytest pytest-asyncio httpx

# Development Server
api:
	@echo "Starting NotifyHubLite API server..."
	@echo "API Documentation: http://localhost:8000/docs"
	@echo "Health Check: http://localhost:8000/health"
	@echo "Press Ctrl+C to stop"
	cd /home/johnnynv/Development/source_code/git/github.com/nvidia/johnnynv/NotifyHubLite && \
	python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# API Documentation
docs:
	@echo "Opening API documentation..."
	@if command -v xdg-open >/dev/null 2>&1; then \
		xdg-open http://localhost:8000/docs; \
	elif command -v open >/dev/null 2>&1; then \
		open http://localhost:8000/docs; \
	else \
		echo "Please open http://localhost:8000/docs in your browser"; \
	fi

# Docker Services
docker-up:
	@echo "Starting Docker services..."
	docker-compose up -d
	@echo "Services started:"
	@echo "  - PostgreSQL: localhost:5432"
	@echo "  - SMTP Server: localhost:25"

docker-down:
	@echo "Stopping Docker services..."
	docker-compose down

docker-logs:
	@echo "Viewing Docker service logs..."
	docker-compose logs -f

# Testing
test:
	@echo "Running tests..."
	pytest -v

email-test:
	@echo "Sending test email via API..."
	@curl -X POST "http://localhost:8000/api/v1/emails/send-plain" \
		-H "Authorization: Bearer notify-hub-api-key-123" \
		-H "Content-Type: application/json" \
		-d '{"recipients":["johnnyj@nvidia.com"],"subject":"NotifyHubLite API Test Email","body":"Hello Johnny,\n\nThis is a test email from NotifyHubLite API system.\n\nSystem Status:\n✅ API service operational\n✅ Authentication working\n✅ Email delivery functional\n✅ SMTP relay connected\n\nThe plain text email feature is working correctly.\n\nPlease confirm receipt of this email.\n\nBest regards,\nNotifyHubLite System","sender_email":"noreply@203.18.50.4.nip.io","sender_name":"NotifyHubLite System"}' \
		| jq .

# Code Quality
lint:
	@echo "Running linting checks..."
	flake8 app/ --max-line-length=120 --ignore=E203,W503

format:
	@echo "Formatting code with black..."
	black app/ --line-length=120

check: lint format test
	@echo "All checks completed!"

# Database
db-init:
	@echo "Initializing database..."
	cd /home/johnnynv/Development/source_code/git/github.com/nvidia/johnnynv/NotifyHubLite && \
	python3 -c "from app.database import create_tables; create_tables()"

# Cleanup
clean:
	@echo "Cleaning cache and temporary files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.log" -delete 2>/dev/null || true
	@echo "Cleanup completed!"

# Health Check
health:
	@echo "Checking API health..."
	curl -s http://localhost:8000/health | jq .

# Show current status
status:
	@echo "NotifyHubLite Status"
	@echo "==================="
	@echo "API Server:"
	@if curl -s http://localhost:8000/health >/dev/null 2>&1; then \
		echo "  ✅ Running on http://localhost:8000"; \
	else \
		echo "  ❌ Not running"; \
	fi
	@echo ""
	@echo "Docker Services:"
	@docker-compose ps 2>/dev/null || echo "  ❌ Docker Compose not available"
	@echo ""
	@echo "Quick Commands:"
	@echo "  make api        - Start API server"
	@echo "  make docs       - Open API documentation"
	@echo "  make email-test - Send test email"
