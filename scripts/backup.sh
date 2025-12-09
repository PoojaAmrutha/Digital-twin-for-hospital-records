# ============================================================================
# FILE: scripts/backup.sh
# Database Backup Script
# ============================================================================

#!/bin/bash

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}HealthWatch AI - Database Backup${NC}"
echo -e "${GREEN}=====================================${NC}"
echo ""

# Create backups directory
BACKUP_DIR="backups"
mkdir -p "$BACKUP_DIR"

# Generate timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/healthwatch_backup_$TIMESTAMP.sql"

echo -e "${YELLOW}📦 Creating database backup...${NC}"

# Backup PostgreSQL database
docker-compose exec -T postgres pg_dump -U healthwatch_user healthwatch_db > "$BACKUP_FILE"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Backup created successfully!${NC}"
    echo -e "${GREEN}📁 Location: $BACKUP_FILE${NC}"
    
    # Get file size
    SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo -e "${GREEN}📊 Size: $SIZE${NC}"
    
    # Compress backup
    echo -e "${YELLOW}🗜️  Compressing backup...${NC}"
    gzip "$BACKUP_FILE"
    
    COMPRESSED_FILE="${BACKUP_FILE}.gz"
    COMPRESSED_SIZE=$(du -h "$COMPRESSED_FILE" | cut -f1)
    
    echo -e "${GREEN}✅ Backup compressed!${NC}"
    echo -e "${GREEN}📁 Location: $COMPRESSED_FILE${NC}"
    echo -e "${GREEN}📊 Compressed size: $COMPRESSED_SIZE${NC}"
    
    # Keep only last 10 backups
    echo -e "${YELLOW}🧹 Cleaning old backups...${NC}"
    ls -t "$BACKUP_DIR"/*.sql.gz 2>/dev/null | tail -n +11 | xargs -r rm
    echo -e "${GREEN}✅ Cleanup completed!${NC}"
    
else
    echo -e "${RED}❌ Backup failed!${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}Backup Process Completed${NC}"
echo -e "${GREEN}=====================================${NC}"


# ============================================================================
# FILE: scripts/deploy.sh
# Production Deployment Script
# ============================================================================

#!/bin/bash

set -e

# Colors
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

# Pull latest changes
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

# Run migrations (if needed)
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


# ============================================================================
# FILE: scripts/restore.sh
# Database Restore Script
# ============================================================================

#!/bin/bash

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}HealthWatch AI - Database Restore${NC}"
echo -e "${GREEN}=====================================${NC}"
echo ""

BACKUP_DIR="backups"

# Check if backup directory exists
if [ ! -d "$BACKUP_DIR" ]; then
    echo -e "${RED}❌ Backup directory not found${NC}"
    exit 1
fi

# List available backups
echo -e "${YELLOW}📂 Available backups:${NC}"
echo ""

backups=($(ls -t "$BACKUP_DIR"/*.sql.gz 2>/dev/null))

if [ ${#backups[@]} -eq 0 ]; then
    echo -e "${RED}❌ No backups found${NC}"
    exit 1
fi

# Display numbered list
for i in "${!backups[@]}"; do
    SIZE=$(du -h "${backups[$i]}" | cut -f1)
    FILENAME=$(basename "${backups[$i]}")
    echo -e "  ${BLUE}[$((i+1))]${NC} $FILENAME (${SIZE})"
done

echo ""
read -p "Enter backup number to restore (or 'q' to quit): " choice

if [ "$choice" == "q" ] || [ "$choice" == "Q" ]; then
    echo -e "${YELLOW}Restore cancelled${NC}"
    exit 0
fi

# Validate choice
if ! [[ "$choice" =~ ^[0-9]+$ ]] || [ "$choice" -lt 1 ] || [ "$choice" -gt ${#backups[@]} ]; then
    echo -e "${RED}❌ Invalid choice${NC}"
    exit 1
fi

SELECTED_BACKUP="${backups[$((choice-1))]}"

echo ""
echo -e "${YELLOW}⚠️  WARNING: This will overwrite the current database!${NC}"
read -p "Are you sure you want to restore from $SELECTED_BACKUP? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo -e "${YELLOW}Restore cancelled${NC}"
    exit 0
fi

echo ""
echo -e "${YELLOW}📦 Restoring database from backup...${NC}"

# Decompress backup if needed
TEMP_FILE="${SELECTED_BACKUP%.gz}"
if [[ "$SELECTED_BACKUP" == *.gz ]]; then
    gunzip -c "$SELECTED_BACKUP" > "$TEMP_FILE"
fi

# Restore database
docker-compose exec -T postgres psql -U healthwatch_user healthwatch_db < "$TEMP_FILE"

# Clean up temp file
if [[ "$SELECTED_BACKUP" == *.gz ]]; then
    rm "$TEMP_FILE"
fi

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Database restored successfully!${NC}"
else
    echo -e "${RED}❌ Restore failed!${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}Restore Process Completed${NC}"
echo -e "${GREEN}=====================================${NC}"