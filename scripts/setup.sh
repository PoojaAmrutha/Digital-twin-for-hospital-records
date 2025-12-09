#!/bin/bash

# ============================================================================
# HEALTHWATCH AI - AUTOMATED SETUP SCRIPT
# ============================================================================
# This script automates the complete setup of HealthWatch AI system
# Run: bash setup.sh
# ============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "${BLUE}"
    echo "============================================================================"
    echo "$1"
    echo "============================================================================"
    echo -e "${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# ============================================================================
# MAIN SETUP
# ============================================================================

print_header "HEALTHWATCH AI - AUTOMATED SETUP"
echo ""
print_info "This script will set up the complete HealthWatch AI system"
echo ""

# ============================================================================
# 1. Check Prerequisites
# ============================================================================
print_header "STEP 1: Checking Prerequisites"

# Check Docker
if command_exists docker; then
    print_success "Docker is installed"
    docker --version
else
    print_error "Docker is not installed"
    print_info "Please install Docker from: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check Docker Compose
if command_exists docker-compose; then
    print_success "Docker Compose is installed"
    docker-compose --version
else
    print_error "Docker Compose is not installed"
    print_info "Please install Docker Compose from: https://docs.docker.com/compose/install/"
    exit 1
fi

# Check Python (for non-Docker setup)
if command_exists python3; then
    print_success "Python 3 is installed"
    python3 --version
else
    print_warning "Python 3 is not installed (optional for Docker setup)"
fi

# Check Node.js (for frontend)
if command_exists node; then
    print_success "Node.js is installed"
    node --version
else
    print_warning "Node.js is not installed (optional for Docker setup)"
fi

echo ""
read -p "Continue with setup? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_info "Setup cancelled"
    exit 0
fi

# ============================================================================
# 2. Create Project Structure
# ============================================================================
print_header "STEP 2: Creating Project Structure"

mkdir -p backend/{tests,datasets/{wesad,apple_watch,fitbit},models}
mkdir -p frontend/{src/{components,services,utils},public}
mkdir -p docs scripts

print_success "Project structure created"

# ============================================================================
# 3. Setup Backend
# ============================================================================
print_header "STEP 3: Setting Up Backend"

cd backend

# Create .env file
if [ ! -f .env ]; then
    cat > .env << EOF
DATABASE_URL=postgresql://healthwatch_user:healthwatch_pass@postgres:5432/healthwatch_db
REDIS_URL=redis://redis:6379
SECRET_KEY=$(openssl rand -hex 32)
ALERT_THRESHOLD_HR_LOW=40
ALERT_THRESHOLD_HR_HIGH=130
ALERT_THRESHOLD_SPO2_LOW=88
ALERT_THRESHOLD_TEMP_HIGH=38.5
EOF
    print_success "Created .env file"
else
    print_info ".env file already exists"
fi

# Create requirements.txt
cat > requirements.txt << EOF
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
redis==5.0.1
pydantic==2.5.0
python-dotenv==1.0.0
numpy==1.26.2
pandas==2.1.3
scikit-learn==1.3.2
tensorflow==2.15.0
joblib==1.3.2
python-multipart==0.0.6
websockets==12.0
pytest==7.4.3
pytest-cov==4.1.0
requests==2.31.0
EOF
print_success "Created requirements.txt"

# Create Dockerfile
cat > Dockerfile << EOF
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p models

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/')"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF
print_success "Created backend Dockerfile"

cd ..

# ============================================================================
# 4. Setup Frontend
# ============================================================================
print_header "STEP 4: Setting Up Frontend"

cd frontend

# Create package.json
cat > package.json << EOF
{
  "name": "healthwatch-ai-frontend",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1",
    "recharts": "^2.10.0",
    "lucide-react": "^0.263.1",
    "axios": "^1.6.0"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "eslintConfig": {
    "extends": ["react-app"]
  },
  "browserslist": {
    "production": [">0.2%", "not dead", "not op_mini all"],
    "development": ["last 1 chrome version"]
  },
  "proxy": "http://localhost:8000"
}
EOF
print_success "Created package.json"

# Create .env
echo "REACT_APP_API_URL=http://localhost:8000" > .env
print_success "Created frontend .env"

# Create Dockerfile
cat > Dockerfile << EOF
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 3000
CMD ["npm", "start"]
EOF
print_success "Created frontend Dockerfile"

cd ..

# ============================================================================
# 5. Create Docker Compose
# ============================================================================
print_header "STEP 5: Creating Docker Compose Configuration"

cat > docker-compose.yml << EOF
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: healthwatch_postgres
    environment:
      POSTGRES_USER: healthwatch_user
      POSTGRES_PASSWORD: healthwatch_pass
      POSTGRES_DB: healthwatch_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - healthwatch_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U healthwatch_user"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: healthwatch_redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - healthwatch_network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: healthwatch_backend
    environment:
      DATABASE_URL: postgresql://healthwatch_user:healthwatch_pass@postgres:5432/healthwatch_db
      REDIS_URL: redis://redis:6379
      SECRET_KEY: your-secret-key-change-in-production
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - healthwatch_network
    volumes:
      - ./backend:/app
      - ./backend/models:/app/models

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: healthwatch_frontend
    ports:
      - "3000:3000"
    environment:
      REACT_APP_API_URL: http://localhost:8000
    depends_on:
      - backend
    networks:
      - healthwatch_network
    volumes:
      - ./frontend:/app
      - /app/node_modules

networks:
  healthwatch_network:
    driver: bridge

volumes:
  postgres_data:
  redis_data:
EOF
print_success "Created docker-compose.yml"

# ============================================================================
# 6. Create Makefile
# ============================================================================
print_header "STEP 6: Creating Makefile"

cat > Makefile << 'EOF'
.PHONY: help build up down logs shell db-init db-reset simulate train clean

help:
	@echo "HealthWatch AI - Available Commands:"
	@echo "  make build        - Build all containers"
	@echo "  make up          - Start all services"
	@echo "  make down        - Stop all services"
	@echo "  make logs        - View logs"
	@echo "  make shell       - Access backend shell"
	@echo "  make db-init     - Initialize database"
	@echo "  make db-reset    - Reset database"
	@echo "  make simulate    - Run data simulation"
	@echo "  make train       - Train ML models"
	@echo "  make clean       - Remove all containers and volumes"

build:
	docker-compose build

up:
	docker-compose up -d
	@echo "✅ Services started!"
	@echo "🔗 Backend API: http://localhost:8000"
	@echo "🔗 Frontend: http://localhost:3000"
	@echo "🔗 API Docs: http://localhost:8000/docs"

down:
	docker-compose down

logs:
	docker-compose logs -f

shell:
	docker-compose exec backend /bin/bash

db-init:
	docker-compose exec backend python run_simulation.py --mode init
	@echo "✅ Database initialized!"

db-reset:
	docker-compose exec backend python run_simulation.py --mode reset
	@echo "✅ Database reset!"

simulate:
	docker-compose exec backend python run_simulation.py --mode simulate --user_id 1 --duration 60

train:
	docker-compose exec backend python run_simulation.py --mode train
	@echo "✅ Models trained!"

clean:
	docker-compose down -v
	@echo "✅ All containers and volumes removed!"
EOF
print_success "Created Makefile"

# ============================================================================
# 7. Create .gitignore
# ============================================================================
print_header "STEP 7: Creating .gitignore"

cat > .gitignore << EOF
# Python
__pycache__/
*.py[cod]
*\$py.class
*.so
.Python
venv/
env/
.venv
ENV/
.env

# Node
node_modules/
/build
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.env.local
.env.development.local
.env.test.local
.env.production.local

# Database
*.db
*.sqlite3
*.log

# ML Models
*.pkl
*.h5
*.joblib

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Docker
.dockerignore

# Coverage
htmlcov/
.coverage
.coverage.*
.pytest_cache/
EOF
print_success "Created .gitignore"

# ============================================================================
# 8. Create README
# ============================================================================
print_header "STEP 8: Creating README"

cat > README.md << 'EOF'
# 🏥 HealthWatch AI - AI-Powered Health Monitoring System

Complete full-stack health monitoring system with real-time vitals tracking, AI anomaly detection, and dual dashboards.

## 🚀 Quick Start

```bash
# Start everything
make build
make up

# Initialize database
make db-init

# Train ML models
make train

# Run simulation
make simulate
```

## 📱 Access

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

## 🎯 Features

✅ Real-time vital monitoring (HR, SpO2, Temperature, Stress)
✅ AI-powered anomaly detection
✅ Automated alert system
✅ Patient dashboard
✅ Hospital monitoring dashboard
✅ Health score calculation (0-100)
✅ Risk prediction models
✅ WebSocket real-time updates

## 📊 Tech Stack

- **Backend:** Python, FastAPI, PostgreSQL, Redis
- **Frontend:** React, Recharts, Tailwind CSS
- **ML:** Scikit-learn, TensorFlow, Isolation Forest
- **DevOps:** Docker, Docker Compose

## 🧪 Commands

```bash
make help          # Show all commands
make build         # Build containers
make up            # Start services
make down          # Stop services
make logs          # View logs
make shell         # Backend shell
make db-init       # Initialize DB
make simulate      # Run simulation
make train         # Train models
make clean         # Clean all
```

## 📝 License

MIT License
EOF
print_success "Created README.md"

# ============================================================================
# 9. Summary & Next Steps
# ============================================================================
print_header "SETUP COMPLETE! 🎉"

echo ""
print_info "Project structure created successfully!"
echo ""
print_warning "NEXT STEPS:"
echo ""
echo "1️⃣  Copy the Python code files from artifacts to backend/"
echo "   - main.py"
echo "   - database.py"
echo "   - models.py"
echo "   - schemas.py"
echo "   - ml_models.py"
echo "   - alert_system.py"
echo "   - redis_client.py"
echo "   - data_simulator.py"
echo "   - dataset_loader.py"
echo "   - run_simulation.py"
echo ""
echo "2️⃣  Copy the React component from artifact to frontend/src/App.js"
echo ""
echo "3️⃣  Build and start the system:"
echo "   ${BLUE}make build${NC}"
echo "   ${BLUE}make up${NC}"
echo ""
echo "4️⃣  Initialize the database:"
echo "   ${BLUE}make db-init${NC}"
echo ""
echo "5️⃣  Train ML models:"
echo "   ${BLUE}make train${NC}"
echo ""
echo "6️⃣  Run the data simulator:"
echo "   ${BLUE}make simulate${NC}"
echo ""
echo "7️⃣  Access the application:"
echo "   Frontend: ${GREEN}http://localhost:3000${NC}"
echo "   Backend:  ${GREEN}http://localhost:8000${NC}"
echo "   API Docs: ${GREEN}http://localhost:8000/docs${NC}"
echo ""
print_success "Happy coding! 🚀"
echo ""

# ============================================================================
# Optional: Auto-start setup
# ============================================================================
echo ""
read -p "Would you like to build and start the system now? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_info "Building containers..."
    make build
    
    print_info "Starting services..."
    make up
    
    sleep 5
    
    print_success "System is running!"
    print_info "Don't forget to run 'make db-init' and 'make train' after copying the code files"
fi