#!/bin/bash

# ============================================================================
# FILE: scripts/deploy.sh
# Production Deployment Script
# ============================================================================

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=====================================${NC}"
echo -e "${BLUE}HealthWatch AI - Deployment Script${NC}"
echo -e "${BLUE}=====================================${NC}"
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    echo -e "${RED}❌ Please do not run as root${NC}"
    exit 1
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo -e "${YELLOW}🔍 Checking prerequisites...${NC}"

if ! command_exists docker; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    exit 1
fi

if ! command_exists docker-compose; then
    echo -e "${RED}❌ Docker Compose is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites satisfied${NC}"
echo ""

# Backup existing database
echo -e "${YELLOW}📦 Creating backup before deployment...${NC}"
if [ -f "scripts/backup.sh" ]; then
    bash scripts/backup.sh
else
    echo -e "${YELLOW}⚠️  Backup script not found, skipping backup${NC}"
fi
echo ""

# Pull latest changes (if using git)
echo -e "${YELLOW}📥 Pulling latest changes...${NC}"
if [ -d ".git" ]; then
    git pull origin main
    echo -e "${GREEN}✅ Changes pulled${NC}"
else
    echo -e "${YELLOW}⚠️  Not a git repository, skipping pull${NC}"
fi
echo ""

# Stop existing containers
echo -e "${YELLOW}🛑 Stopping existing services...${NC}"
docker-compose down
echo -e "${GREEN}✅ Services stopped${NC}"
echo ""

# Build new images
echo -e "${YELLOW}🔨 Building Docker images...${NC}"
docker-compose build --no-cache
echo -e "${GREEN}✅ Images built${NC}"
echo ""

# Start services
echo -e "${YELLOW}🚀 Starting services...${NC}"
docker-compose up -d
echo -e "${GREEN}✅ Services started${NC}"
echo ""

# Wait for services to be ready
echo -e "${YELLOW}⏳ Waiting for services to be ready...${NC}"
sleep 10

# Check service health
echo -e "${YELLOW}🏥 Checking service health...${NC}"

# Check backend
BACKEND_HEALTH=$(curl -s http://localhost:8000/ | grep -o "healthy" || echo "")
if [ "$BACKEND_HEALTH" == "healthy" ]; then
    echo -e "${GREEN}✅ Backend is healthy${NC}"
else
    echo -e "${RED}❌ Backend health check failed${NC}"
fi

# Check frontend
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 || echo "000")
if [ "$FRONTEND_STATUS" == "200" ]; then
    echo -e "${GREEN}✅ Frontend is accessible${NC}"
else
    echo -e "${YELLOW}⚠️  Frontend status: $FRONTEND_STATUS${NC}"
fi

# Check database
DB_STATUS=$(docker-compose exec -T postgres pg_isready -U healthwatch_user || echo "")
if [[ "$DB_STATUS" == *"accepting connections"* ]]; then
    echo -e "${GREEN}✅ Database is ready${NC}"
else
    echo -e "${RED}❌ Database is not ready${NC}"
fi

# Check Redis
REDIS_STATUS=$(docker-compose exec -T redis redis-cli ping || echo "")
if [ "$REDIS_STATUS" == "PONG" ]; then
    echo -e "${GREEN}✅ Redis is ready${NC}"
else
    echo -e "${RED}❌ Redis is not ready${NC}"
fi

echo ""

# Run migrations
echo -e "${YELLOW}🔄 Running database migrations...${NC}"
docker-compose exec backend python -c "from database import init_db; init_db()"
echo -e "${GREEN}✅ Migrations completed${NC}"
echo ""

# Clean up old images
echo -e "${YELLOW}🧹 Cleaning up old images...${NC}"
docker image prune -f
echo -e "${GREEN}✅ Cleanup completed${NC}"
echo ""

# Display service URLs
echo -e "${BLUE}=====================================${NC}"
echo -e "${BLUE}Deployment Completed Successfully!${NC}"
echo -e "${BLUE}=====================================${NC}"
echo ""
echo -e "${GREEN}🔗 Access URLs:${NC}"
echo -e "   Frontend:     ${BLUE}http://localhost:3000${NC}"
echo -e "   Backend API:  ${BLUE}http://localhost:8000${NC}"
echo -e "   API Docs:     ${BLUE}http://localhost:8000/docs${NC}"
echo ""
echo -e "${GREEN}📊 Service Status:${NC}"
docker-compose ps
echo ""
echo -e "${GREEN}📝 View logs: ${BLUE}docker-compose logs -f${NC}"
echo -e "${GREEN}🛑 Stop services: ${BLUE}docker-compose down${NC}"
echo ""