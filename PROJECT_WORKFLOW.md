# HealthWatch AI - Complete Project Workflow

## 📋 Table of Contents
- [Project Overview](#project-overview)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Setup & Installation](#setup--installation)
- [Running the Application](#running-the-application)
- [Development Workflows](#development-workflows)
- [Testing & Verification](#testing--verification)
- [Database Management](#database-management)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Project Overview

**HealthWatch AI** is a Digital Twin system for hospital records that enables predictive healthcare analytics. The system creates virtual representations of patient health data to enable proactive healthcare management, reduce readmissions, and improve treatment outcomes through data-driven decision-making.

### Key Features
- **Digital Twin Creation**: Virtual representations of patient health records
- **LLM-based Entity Extraction**: Automated extraction of medical entities from clinical notes
- **Predictive Analytics**: ML models for risk assessment and health predictions
- **Real-time Monitoring**: Continuous patient vital signs tracking
- **Role-based Access**: Separate interfaces for patients and doctors
- **Interactive Dashboards**: Visualizations for health metrics and trends
- **AI Chatbot**: Patient symptom analysis and health guidance

---

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL (with SQLAlchemy ORM)
- **Caching**: Redis
- **ML/AI**: 
  - scikit-learn (predictive models)
  - Gemini AI (LLM for entity extraction)
  - TensorFlow/PyTorch (deep learning models)
- **API Documentation**: Swagger/OpenAPI

### Frontend
- **Framework**: React.js
- **Styling**: CSS3 with modern design patterns
- **Charts**: Chart.js / Recharts
- **State Management**: React Hooks

### DevOps
- **Containerization**: Docker & Docker Compose
- **Build Tool**: Make
- **Testing**: pytest
- **Version Control**: Git

### Machine Learning Algorithms
1. **Risk Assessment Model**: Classification model for patient risk levels
2. **Readmission Prediction**: Predicts likelihood of hospital readmission
3. **Vital Signs Forecasting**: Time-series prediction for patient vitals
4. **Entity Extraction**: NLP model for medical entity recognition
5. **Anomaly Detection**: Identifies unusual patterns in patient data

---

## 📁 Project Structure

```
AIML_lab_project/
├── backend/                    # FastAPI backend application
│   ├── main.py                # Main API endpoints
│   ├── models.py              # Database models
│   ├── schemas.py             # Pydantic schemas
│   ├── database.py            # Database configuration
│   ├── ml_models.py           # Machine learning models
│   ├── llm_service.py         # LLM integration
│   ├── alert_system.py        # Alert and notification system
│   ├── data_similator.py      # Data simulation utilities
│   ├── redis_client.py        # Redis caching
│   ├── requirements.txt       # Python dependencies
│   └── tests/                 # Backend tests
│
├── frontend/                   # React frontend application
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── pages/             # Page components
│   │   └── App.js             # Main app component
│   ├── public/                # Static assets
│   └── package.json           # Node dependencies
│
├── .agent/workflows/          # Workflow automation scripts
│   ├── start_backend.md       # Backend startup workflow
│   └── verify_digital_twin.md # Verification workflow
│
├── scripts/                   # Utility scripts
├── docker-compose.yml         # Docker services configuration
├── Makefile                   # Build and automation commands
└── healthwatch.db            # SQLite database (development)
```

---

## 🚀 Setup & Installation

### Prerequisites
- **Docker** & **Docker Compose** (recommended)
- **Python 3.9+** (for local development)
- **Node.js 16+** & **npm** (for frontend)
- **PostgreSQL** (if not using Docker)
- **Redis** (if not using Docker)

### Option 1: Docker Setup (Recommended)

#### 1. Complete Initial Setup
```bash
make setup
```
This command will:
- Build all Docker containers
- Start all services
- Initialize the database
- Train ML models

#### 2. Individual Setup Steps
If you prefer to run steps individually:

```bash
# Build Docker containers
make build

# Start all services
make up

# Initialize database
make db-init

# Train ML models
make train
```

### Option 2: Local Development Setup

#### 1. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\Activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### 2. Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install
```

#### 3. Environment Configuration
Create a `.env` file in the backend directory:
```env
DATABASE_URL=postgresql://healthwatch_user:password@localhost:5432/healthwatch_db
REDIS_URL=redis://localhost:6379
GEMINI_API_KEY=your_gemini_api_key_here
SECRET_KEY=your_secret_key_here
```

---

## 🏃 Running the Application

### Using Docker (Recommended)

#### Start All Services
```bash
make up
```

**Access URLs:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- PostgreSQL: localhost:5432
- Redis: localhost:6379

#### Stop All Services
```bash
make down
```

#### Restart Services
```bash
make restart
```

#### View Logs
```bash
# All services
make logs

# Backend only
make logs-backend

# Frontend only
make logs-frontend

# Database only
make logs-db
```

### Local Development

#### Start Backend Server
```bash
cd backend

# Activate virtual environment
.\venv\Scripts\Activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Run server with auto-reload
uvicorn main:app --reload
```

The API will be available at:
- API: http://127.0.0.1:8000
- Documentation: http://127.0.0.1:8000/docs

#### Start Frontend Development Server
```bash
cd frontend

# Start development server
npm start
```

The frontend will be available at http://localhost:3000

---

## 🔄 Development Workflows

### Workflow 1: Start Backend Server

1. Open a terminal
2. Navigate to the backend directory:
   ```powershell
   cd backend
   ```
3. (Optional) Create and activate a virtual environment:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate
   ```
4. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
5. Run the server using Uvicorn:
   ```powershell
   uvicorn main:app --reload
   ```
6. The API will be available at `http://127.0.0.1:8000`
7. Access the interactive documentation at `http://127.0.0.1:8000/docs`

### Workflow 2: Manual Verification of Digital Twin Flow

1. **Start the Server** (see Workflow 1 above)

2. **Open Swagger UI**: Go to `http://127.0.0.1:8000/docs` in your browser

3. **Create a Doctor**:
   - Expand `POST /users/`
   - Click "Try it out"
   - Use this JSON:
     ```json
     {
       "name": "Dr. House",
       "email": "house@hospital.com",
       "age": 45,
       "gender": "M",
       "user_type": "doctor"
     }
     ```
   - Execute and copy the `id` (likely `1`)

4. **Create a Patient**:
   - Use this JSON:
     ```json
     {
       "name": "John Doe",
       "email": "john@example.com",
       "age": 30,
       "gender": "M",
       "user_type": "patient"
     }
     ```
   - Execute and copy the `id` (likely `2`)

5. **Create a Medical Record**:
   - Expand `POST /medical-records/`
   - Set `current_user_id` to the Doctor's ID (`1`)
   - Use this JSON:
     ```json
     {
       "record_type": "note",
       "content": "Patient complains of excessive thirst and fatigue. Possible diabetes.",
       "user_id": 2
     }
     ```
   - Execute

6. **View Digital Twin**:
   - Expand `GET /digital-twin/{user_id}`
   - Set `user_id` to the Patient's ID (`2`)
   - Execute
   - Verify that the response includes:
     - **Risk Assessment**
     - **Extracted Entities** (e.g., Diabetes)

### Workflow 3: Data Simulation

#### Full Simulation (60 minutes)
```bash
make simulate
```

#### Short Simulation (10 minutes)
```bash
make simulate-short
```

#### Custom Simulation
```bash
docker-compose exec backend python run_simulation.py --mode simulate --user_id 1 --duration 30
```

### Workflow 4: Model Training

```bash
# Train all ML models
make train

# Or manually
docker-compose exec backend python run_simulation.py --mode train
```

---

## 🧪 Testing & Verification

### Run All Tests
```bash
make test
```

### Run Tests with Coverage
```bash
make test-coverage
```

### Run Specific Test Suites
```bash
# API tests only
make test-api

# ML model tests only
make test-ml
```

### Manual Testing via Swagger UI
1. Start the backend server
2. Navigate to http://localhost:8000/docs
3. Test endpoints interactively

---

## 🗄️ Database Management

### Initialize Database
```bash
make db-init
```

### Reset Database (⚠️ Deletes all data)
```bash
make db-reset
```

### Backup Database
```bash
make db-backup
```
Backups are stored in the `backups/` directory with timestamps.

### Restore Database
```bash
make db-restore
```
You'll be prompted to select a backup file.

### Access Database Shell
```bash
# PostgreSQL shell
make db-shell

# Database container shell
make shell-db
```

---

## 🐳 Docker Commands

### Service Management
```bash
# Check service status
make status

# List all containers
make ps

# View resource usage
make stats

# View running processes
make top
```

### Shell Access
```bash
# Backend container shell
make shell

# Database container shell
make shell-db
```

### Cleanup
```bash
# Remove containers and volumes
make clean

# Remove everything (including images)
make clean-all

# Clean Python cache
make clean-cache
```

---

## 🚢 Deployment

### Production Build
```bash
make prod-build
```

### Start Production Services
```bash
make prod-up
```

### Stop Production Services
```bash
make prod-down
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Stop all services
make down

# Check for processes using ports
# Windows:
netstat -ano | findstr :8000
netstat -ano | findstr :3000

# Kill the process
taskkill /PID <process_id> /F
```

#### 2. Database Connection Issues
```bash
# Reset database
make db-reset

# Reinitialize
make db-init
```

#### 3. Docker Issues
```bash
# Clean everything and start fresh
make fresh-start
```

#### 4. Frontend Not Loading
```bash
# Reinstall dependencies
cd frontend
rm -rf node_modules package-lock.json
npm install
```

#### 5. Backend Dependencies Issues
```bash
cd backend
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### Logs and Debugging

```bash
# View all logs
make logs

# View specific service logs
make logs-backend
make logs-frontend
make logs-db

# Follow logs in real-time
docker-compose logs -f backend
```

---

## 📊 Quick Reference Commands

### Development Shortcuts
```bash
# Start development mode (up + logs)
make dev

# Quick test (init + train + test)
make quick-test

# Fresh start (clean + build + setup)
make fresh-start
```

### Most Used Commands
```bash
make help          # Show all available commands
make setup         # Complete initial setup
make up            # Start all services
make down          # Stop all services
make logs          # View logs
make test          # Run tests
make db-backup     # Backup database
make clean         # Clean up
```

---

## 📝 Additional Notes

### Environment Variables
Key environment variables to configure:
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `GEMINI_API_KEY`: Google Gemini API key for LLM features
- `SECRET_KEY`: Application secret key

### API Endpoints
Main API endpoints:
- `POST /users/`: Create user (patient/doctor)
- `GET /users/{user_id}`: Get user details
- `POST /medical-records/`: Create medical record
- `GET /digital-twin/{user_id}`: Get patient's digital twin
- `GET /predictions/{user_id}`: Get health predictions
- `POST /chat/`: Chatbot interaction

### Development Tips
1. Always use virtual environments for Python development
2. Run tests before committing changes
3. Use `make logs` to debug issues
4. Backup database before major changes
5. Use Swagger UI for API testing

---

## 🤝 Contributing
1. Create a feature branch
2. Make your changes
3. Run tests: `make test`
4. Submit a pull request

---

## 📄 License
[Add your license information here]

---

## 📞 Support
For issues and questions, please refer to the project documentation or contact the development team.

---

**Last Updated**: December 2025
**Version**: 1.0.0
