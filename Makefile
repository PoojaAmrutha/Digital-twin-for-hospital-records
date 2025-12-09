# ============================================================================
# FILE: Makefile
# Convenient Commands for HealthWatch AI Project
# ============================================================================

.PHONY: help build up down restart logs shell db-init db-reset db-backup simulate train test clean frontend-install backend-install

# Default target
.DEFAULT_GOAL := help

help:
	@echo "================================================================"
	@echo "HealthWatch AI - Available Commands"
	@echo "================================================================"
	@echo ""
	@echo "Setup Commands:"
	@echo "  make install         - Install all dependencies"
	@echo "  make build          - Build all Docker containers"
	@echo "  make setup          - Complete initial setup"
	@echo ""
	@echo "Service Commands:"
	@echo "  make up             - Start all services"
	@echo "  make down           - Stop all services"
	@echo "  make restart        - Restart all services"
	@echo "  make logs           - View logs (all services)"
	@echo "  make logs-backend   - View backend logs only"
	@echo "  make logs-frontend  - View frontend logs only"
	@echo ""
	@echo "Database Commands:"
	@echo "  make db-init        - Initialize database"
	@echo "  make db-reset       - Reset database (WARNING: deletes data)"
	@echo "  make db-backup      - Backup database"
	@echo "  make db-restore     - Restore database from backup"
	@echo "  make db-shell       - Open PostgreSQL shell"
	@echo ""
	@echo "Development Commands:"
	@echo "  make shell          - Access backend shell"
	@echo "  make simulate       - Run data simulation (60 min)"
	@echo "  make train          - Train ML models"
	@echo "  make test           - Run all tests"
	@echo "  make test-coverage  - Run tests with coverage report"
	@echo ""
	@echo "Utility Commands:"
	@echo "  make clean          - Remove containers and volumes"
	@echo "  make clean-all      - Remove everything including images"
	@echo "  make status         - Show service status"
	@echo "  make ps             - List all containers"
	@echo ""
	@echo "================================================================"

# ============================================================================
# Installation Commands
# ============================================================================

install: backend-install frontend-install
	@echo "✅ All dependencies installed!"

backend-install:
	@echo "📦 Installing backend dependencies..."
	cd backend && pip install -r requirements.txt
	@echo "✅ Backend dependencies installed!"

frontend-install:
	@echo "📦 Installing frontend dependencies..."
	cd frontend && npm install
	@echo "✅ Frontend dependencies installed!"

# ============================================================================
# Docker Commands
# ============================================================================

build:
	@echo "🔨 Building Docker containers..."
	docker-compose build --no-cache
	@echo "✅ Containers built successfully!"

up:
	@echo "🚀 Starting all services..."
	docker-compose up -d
	@sleep 3
	@echo ""
	@echo "✅ Services started successfully!"
	@echo ""
	@echo "🔗 Access URLs:"
	@echo "   Frontend:     http://localhost:3000"
	@echo "   Backend API:  http://localhost:8000"
	@echo "   API Docs:     http://localhost:8000/docs"
	@echo "   PostgreSQL:   localhost:5432"
	@echo "   Redis:        localhost:6379"
	@echo ""

down:
	@echo "🛑 Stopping all services..."
	docker-compose down
	@echo "✅ Services stopped!"

restart: down up
	@echo "♻️  Services restarted!"

logs:
	docker-compose logs -f

logs-backend:
	docker-compose logs -f backend

logs-frontend:
	docker-compose logs -f frontend

logs-db:
	docker-compose logs -f postgres

# ============================================================================
# Database Commands
# ============================================================================

db-init:
	@echo "🗄️  Initializing database..."
	docker-compose exec backend python run_simulation.py --mode init
	@echo "✅ Database initialized!"

db-reset:
	@echo "⚠️  WARNING: This will delete all data!"
	@read -p "Are you sure? [y/N] " confirm; \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		docker-compose exec backend python run_simulation.py --mode reset; \
		echo "✅ Database reset completed!"; \
	else \
		echo "❌ Database reset cancelled."; \
	fi

db-backup:
	@echo "💾 Creating database backup..."
	@mkdir -p backups
	docker-compose exec postgres pg_dump -U healthwatch_user healthwatch_db > backups/backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "✅ Backup created in backups/ directory"

db-restore:
	@echo "📂 Available backups:"
	@ls -1 backups/*.sql 2>/dev/null || echo "No backups found"
	@read -p "Enter backup filename: " backup; \
	if [ -f "backups/$$backup" ]; then \
		docker-compose exec -T postgres psql -U healthwatch_user healthwatch_db < "backups/$$backup"; \
		echo "✅ Database restored from $$backup"; \
	else \
		echo "❌ Backup file not found"; \
	fi

db-shell:
	docker-compose exec postgres psql -U healthwatch_user healthwatch_db

# ============================================================================
# Development Commands
# ============================================================================

shell:
	@echo "🐚 Opening backend shell..."
	docker-compose exec backend /bin/bash

shell-db:
	@echo "🐚 Opening database shell..."
	docker-compose exec postgres /bin/bash

simulate:
	@echo "📊 Starting data simulation (60 minutes)..."
	docker-compose exec backend python run_simulation.py --mode simulate --user_id 1 --duration 60

simulate-short:
	@echo "📊 Starting short data simulation (10 minutes)..."
	docker-compose exec backend python run_simulation.py --mode simulate --user_id 1 --duration 10

train:
	@echo "🤖 Training ML models..."
	docker-compose exec backend python run_simulation.py --mode train
	@echo "✅ Models trained successfully!"

# ============================================================================
# Testing Commands
# ============================================================================

test:
	@echo "🧪 Running all tests..."
	docker-compose exec backend pytest tests/ -v
	@echo "✅ Tests completed!"

test-coverage:
	@echo "🧪 Running tests with coverage..."
	docker-compose exec backend pytest tests/ -v --cov=. --cov-report=html --cov-report=term-missing
	@echo "✅ Coverage report generated in htmlcov/"

test-api:
	@echo "🧪 Testing API endpoints..."
	docker-compose exec backend pytest tests/test_api.py -v

test-ml:
	@echo "🧪 Testing ML models..."
	docker-compose exec backend pytest tests/test_ml_models.py -v

# ============================================================================
# Setup Commands
# ============================================================================

setup: build up db-init train
	@echo ""
	@echo "🎉 Setup completed successfully!"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Open frontend: http://localhost:3000"
	@echo "  2. Check API docs: http://localhost:8000/docs"
	@echo "  3. Run simulation: make simulate"
	@echo ""

# ============================================================================
# Utility Commands
# ============================================================================

status:
	@echo "📊 Service Status:"
	@docker-compose ps

ps:
	docker-compose ps

clean:
	@echo "🧹 Cleaning up containers and volumes..."
	docker-compose down -v
	@echo "✅ Cleanup completed!"

clean-all:
	@echo "🧹 Removing everything (containers, volumes, images)..."
	docker-compose down -v --rmi all
	@echo "✅ Complete cleanup done!"

clean-cache:
	@echo "🧹 Cleaning Python cache..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "✅ Cache cleaned!"

# ============================================================================
# Monitoring Commands
# ============================================================================

stats:
	docker stats

top:
	docker-compose top

# ============================================================================
# Production Commands
# ============================================================================

prod-build:
	@echo "🏭 Building for production..."
	docker-compose -f docker-compose.prod.yml build

prod-up:
	@echo "🚀 Starting production services..."
	docker-compose -f docker-compose.prod.yml up -d

prod-down:
	docker-compose -f docker-compose.prod.yml down

# ============================================================================
# Development Shortcuts
# ============================================================================

dev: up logs

quick-test: db-init train test

fresh-start: clean-all build setup