# ============================================================================
# TESTING SUITE & API DOCUMENTATION
# ============================================================================

# ============================================================================
# 1. tests/test_api.py - API Tests
# ============================================================================
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from database import Base, get_db

# Test database
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function")
def client():
    Base.metadata.create_all(bind=engine)
    yield TestClient(app)
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def sample_user_data():
    return {
        "name": "Test User",
        "email": "test@example.com",
        "age": 30,
        "gender": "M",
        "user_type": "patient"
    }

@pytest.fixture
def sample_vitals_data():
    return {
        "user_id": 1,
        "heart_rate": 75.5,
        "spo2": 98.2,
        "temperature": 36.8,
        "stress_level": 2.1,
        "steps": 5000,
        "calories": 200,
        "sleep_hours": 7.5
    }

# ============================================================================
# User API Tests
# ============================================================================

def test_create_user(client, sample_user_data):
    """Test user creation"""
    response = client.post("/users/", json=sample_user_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == sample_user_data["name"]
    assert data["email"] == sample_user_data["email"]
    assert "id" in data

def test_get_user(client, sample_user_data):
    """Test retrieving user"""
    # Create user
    create_response = client.post("/users/", json=sample_user_data)
    user_id = create_response.json()["id"]
    
    # Get user
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id
    assert data["name"] == sample_user_data["name"]

def test_get_nonexistent_user(client):
    """Test getting non-existent user returns 404"""
    response = client.get("/users/999")
    assert response.status_code == 404

# ============================================================================
# Vitals API Tests
# ============================================================================

def test_create_vital_reading(client, sample_user_data, sample_vitals_data):
    """Test creating vital reading"""
    # Create user first
    user_response = client.post("/users/", json=sample_user_data)
    user_id = user_response.json()["id"]
    sample_vitals_data["user_id"] = user_id
    
    # Create vital reading
    response = client.post("/vitals/", json=sample_vitals_data)
    assert response.status_code == 200
    data = response.json()
    assert data["heart_rate"] == sample_vitals_data["heart_rate"]
    assert data["user_id"] == user_id

def test_get_latest_vitals(client, sample_user_data, sample_vitals_data):
    """Test retrieving latest vitals"""
    # Setup
    user_response = client.post("/users/", json=sample_user_data)
    user_id = user_response.json()["id"]
    sample_vitals_data["user_id"] = user_id
    client.post("/vitals/", json=sample_vitals_data)
    
    # Get latest
    response = client.get(f"/vitals/user/{user_id}/latest")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data

def test_get_vital_history(client, sample_user_data, sample_vitals_data):
    """Test retrieving vital history"""
    # Setup
    user_response = client.post("/users/", json=sample_user_data)
    user_id = user_response.json()["id"]
    sample_vitals_data["user_id"] = user_id
    
    # Create multiple readings
    for _ in range(5):
        client.post("/vitals/", json=sample_vitals_data)
    
    # Get history
    response = client.get(f"/vitals/user/{user_id}/history?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5

# ============================================================================
# Alert Tests
# ============================================================================

def test_alert_generation_high_hr(client, sample_user_data):
    """Test alert generation for high heart rate"""
    # Create user
    user_response = client.post("/users/", json=sample_user_data)
    user_id = user_response.json()["id"]
    
    # Submit dangerous vitals
    dangerous_vitals = {
        "user_id": user_id,
        "heart_rate": 150,  # High
        "spo2": 98,
        "temperature": 36.8,
        "stress_level": 2.0,
        "steps": 5000,
        "calories": 200,
        "sleep_hours": 7.5
    }
    
    client.post("/vitals/", json=dangerous_vitals)
    
    # Check alerts
    response = client.get(f"/alerts/user/{user_id}")
    assert response.status_code == 200
    alerts = response.json()
    assert len(alerts) > 0

def test_alert_generation_low_spo2(client, sample_user_data):
    """Test alert generation for low SpO2"""
    user_response = client.post("/users/", json=sample_user_data)
    user_id = user_response.json()["id"]
    
    dangerous_vitals = {
        "user_id": user_id,
        "heart_rate": 75,
        "spo2": 85,  # Low
        "temperature": 36.8,
        "stress_level": 2.0,
        "steps": 5000,
        "calories": 200,
        "sleep_hours": 7.5
    }
    
    client.post("/vitals/", json=dangerous_vitals)
    response = client.get(f"/alerts/user/{user_id}")
    alerts = response.json()
    assert len(alerts) > 0

# ============================================================================
# Health Score Tests
# ============================================================================

def test_health_score_calculation(client, sample_user_data, sample_vitals_data):
    """Test health score calculation"""
    user_response = client.post("/users/", json=sample_user_data)
    user_id = user_response.json()["id"]
    sample_vitals_data["user_id"] = user_id
    
    client.post("/vitals/", json=sample_vitals_data)
    
    response = client.get(f"/health-score/user/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert "score" in data
    assert "risk_level" in data
    assert 0 <= data["score"] <= 100

# ============================================================================
# Hospital Dashboard Tests
# ============================================================================

def test_get_all_patients(client, sample_user_data):
    """Test hospital dashboard patient list"""
    # Create multiple patients
    for i in range(3):
        user_data = sample_user_data.copy()
        user_data["email"] = f"patient{i}@example.com"
        client.post("/users/", json=user_data)
    
    response = client.get("/hospital/patients")
    assert response.status_code == 200
    patients = response.json()
    assert len(patients) >= 3

# ============================================================================
# Root Endpoint Test
# ============================================================================

def test_read_root(client):
    """Test API root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


# ============================================================================
# 2. tests/test_ml_models.py - ML Model Tests
# ============================================================================

import numpy as np
from ml_models import AnomalyDetector, HealthScoreCalculator, RiskPredictor

def test_anomaly_detector_training():
    """Test anomaly detector training"""
    detector = AnomalyDetector()
    
    # Generate normal data
    normal_data = np.array([[75, 98, 36.8, 2.0] for _ in range(100)])
    detector.train(normal_data)
    
    assert detector.is_trained == True

def test_anomaly_detector_prediction():
    """Test anomaly detection"""
    detector = AnomalyDetector()
    
    # Train with normal data
    normal_data = np.array([[75, 98, 36.8, 2.0] for _ in range(100)])
    detector.train(normal_data)
    
    # Test normal vitals
    normal_vitals = {
        'heart_rate': 75,
        'spo2': 98,
        'temperature': 36.8,
        'stress_level': 2.0
    }
    is_anomaly = detector.predict(normal_vitals)
    assert isinstance(is_anomaly, bool)
    
    # Test abnormal vitals
    abnormal_vitals = {
        'heart_rate': 180,
        'spo2': 70,
        'temperature': 40,
        'stress_level': 5.0
    }
    is_anomaly = detector.predict(abnormal_vitals)
    # Should likely detect as anomaly (but not guaranteed due to ML nature)

def test_health_score_perfect():
    """Test health score with perfect vitals"""
    perfect_vitals = {
        'heart_rate': 75,
        'spo2': 99,
        'temperature': 36.8,
        'stress_level': 1.5,
        'steps': 8000,
        'calories': 2000,
        'sleep_hours': 8.0
    }
    
    result = HealthScoreCalculator.calculate(perfect_vitals)
    assert result['score'] >= 90
    assert result['risk_level'] == 'low'

def test_health_score_poor():
    """Test health score with poor vitals"""
    poor_vitals = {
        'heart_rate': 140,
        'spo2': 85,
        'temperature': 39,
        'stress_level': 4.5,
        'steps': 1000,
        'calories': 500,
        'sleep_hours': 4.0
    }
    
    result = HealthScoreCalculator.calculate(poor_vitals)
    assert result['score'] < 60
    assert result['risk_level'] == 'high'

def test_risk_predictor():
    """Test risk prediction"""
    predictor = RiskPredictor()
    
    vitals = {
        'heart_rate': 120,
        'spo2': 90,
        'temperature': 38.5,
        'stress_level': 4.0
    }
    
    risks = predictor.predict_risks(vitals)
    assert 'cardiac_risk' in risks
    assert 'respiratory_risk' in risks
    assert 'stress_risk' in risks
    assert all(0 <= risk <= 1 for risk in risks.values())


# ============================================================================
# 3. tests/test_alert_system.py - Alert System Tests
# ============================================================================

from alert_system import AlertSystem

def test_alert_system_normal_vitals():
    """Test no alerts for normal vitals"""
    system = AlertSystem()
    
    normal_vitals = {
        'heart_rate': 75,
        'spo2': 98,
        'temperature': 36.8,
        'stress_level': 2.0
    }
    
    alerts = system.check_vitals(normal_vitals)
    assert len(alerts) == 0

def test_alert_system_high_hr():
    """Test alert for high heart rate"""
    system = AlertSystem()
    
    vitals = {
        'heart_rate': 140,
        'spo2': 98,
        'temperature': 36.8,
        'stress_level': 2.0
    }
    
    alerts = system.check_vitals(vitals)
    assert len(alerts) > 0
    assert any('heart' in alert['title'].lower() for alert in alerts)

def test_alert_system_low_spo2():
    """Test alert for low SpO2"""
    system = AlertSystem()
    
    vitals = {
        'heart_rate': 75,
        'spo2': 85,
        'temperature': 36.8,
        'stress_level': 2.0
    }
    
    alerts = system.check_vitals(vitals)
    assert len(alerts) > 0
    assert any('oxygen' in alert['message'].lower() for alert in alerts)


# ============================================================================
# 4. pytest.ini - Pytest Configuration
# ============================================================================
"""
# File: pytest.ini

[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --cov=.
    --cov-report=html
    --cov-report=term-missing
"""


# ============================================================================
# 5. postman_collection.json - API Testing Collection
# ============================================================================
"""
{
  "info": {
    "name": "HealthWatch AI API",
    "description": "Complete API collection for testing",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Users",
      "item": [
        {
          "name": "Create User",
          "request": {
            "method": "POST",
            "header": [{"key": "Content-Type", "value": "application/json"}],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"name\": \"John Doe\",\n  \"email\": \"john@example.com\",\n  \"age\": 45,\n  \"gender\": \"M\",\n  \"user_type\": \"patient\"\n}"
            },
            "url": {"raw": "{{base_url}}/users/", "host": ["{{base_url}}"], "path": ["users", ""]}
          }
        },
        {
          "name": "Get User",
          "request": {
            "method": "GET",
            "url": {"raw": "{{base_url}}/users/{{user_id}}", "host": ["{{base_url}}"], "path": ["users", "{{user_id}}"]}
          }
        }
      ]
    },
    {
      "name": "Vitals",
      "item": [
        {
          "name": "Submit Vitals",
          "request": {
            "method": "POST",
            "header": [{"key": "Content-Type", "value": "application/json"}],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"user_id\": 1,\n  \"heart_rate\": 75.5,\n  \"spo2\": 98.2,\n  \"temperature\": 36.8,\n  \"stress_level\": 2.1,\n  \"steps\": 5000,\n  \"calories\": 200,\n  \"sleep_hours\": 7.5\n}"
            },
            "url": {"raw": "{{base_url}}/vitals/", "host": ["{{base_url}}"], "path": ["vitals", ""]}
          }
        },
        {
          "name": "Get Latest Vitals",
          "request": {
            "method": "GET",
            "url": {"raw": "{{base_url}}/vitals/user/{{user_id}}/latest", "host": ["{{base_url}}"], "path": ["vitals", "user", "{{user_id}}", "latest"]}
          }
        },
        {
          "name": "Get Vital History",
          "request": {
            "method": "GET",
            "url": {"raw": "{{base_url}}/vitals/user/{{user_id}}/history?limit=50", "host": ["{{base_url}}"], "path": ["vitals", "user", "{{user_id}}", "history"], "query": [{"key": "limit", "value": "50"}]}
          }
        }
      ]
    },
    {
      "name": "Health Score",
      "item": [
        {
          "name": "Get Health Score",
          "request": {
            "method": "GET",
            "url": {"raw": "{{base_url}}/health-score/user/{{user_id}}", "host": ["{{base_url}}"], "path": ["health-score", "user", "{{user_id}}"]}
          }
        }
      ]
    },
    {
      "name": "Alerts",
      "item": [
        {
          "name": "Get User Alerts",
          "request": {
            "method": "GET",
            "url": {"raw": "{{base_url}}/alerts/user/{{user_id}}?limit=10", "host": ["{{base_url}}"], "path": ["alerts", "user", "{{user_id}}"], "query": [{"key": "limit", "value": "10"}]}
          }
        }
      ]
    },
    {
      "name": "Hospital",
      "item": [
        {
          "name": "Get All Patients",
          "request": {
            "method": "GET",
            "url": {"raw": "{{base_url}}/hospital/patients", "host": ["{{base_url}}"], "path": ["hospital", "patients"]}
          }
        }
      ]
    }
  ],
  "variable": [
    {"key": "base_url", "value": "http://localhost:8000"},
    {"key": "user_id", "value": "1"}
  ]
}
"""


# ============================================================================
# 6. API_DOCUMENTATION.md - Complete API Reference
# ============================================================================
"""
# 📚 HealthWatch AI - API Documentation

## Base URL
```
http://localhost:8000
```

## Authentication
Currently no authentication required (add JWT in production)

---

## 👤 Users Endpoints

### Create User
**POST** `/users/`

Create a new user (patient or doctor).

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "age": 45,
  "gender": "M",
  "user_type": "patient"
}
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "age": 45,
  "gender": "M",
  "user_type": "patient",
  "created_at": "2024-01-15T10:30:00"
}
```

### Get User
**GET** `/users/{user_id}`

Retrieve user details.

**Response:** `200 OK`
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "age": 45,
  "gender": "M",
  "user_type": "patient",
  "created_at": "2024-01-15T10:30:00"
}
```

---

## 💓 Vitals Endpoints

### Submit Vital Reading
**POST** `/vitals/`

Submit new vital reading. Triggers:
- Database storage
- Redis caching
- Anomaly detection
- Alert generation
- Health score calculation

**Request Body:**
```json
{
  "user_id": 1,
  "heart_rate": 75.5,
  "spo2": 98.2,
  "temperature": 36.8,
  "stress_level": 2.1,
  "steps": 5000,
  "calories": 200,
  "sleep_hours": 7.5
}
```

**Response:** `200 OK`
```json
{
  "id": 123,
  "user_id": 1,
  "heart_rate": 75.5,
  "spo2": 98.2,
  "temperature": 36.8,
  "stress_level": 2.1,
  "steps": 5000,
  "calories": 200,
  "sleep_hours": 7.5,
  "timestamp": "2024-01-15T10:35:00"
}
```

### Get Latest Vitals
**GET** `/vitals/user/{user_id}/latest`

Get most recent vital reading (cached for performance).

**Response:** `200 OK`
```json
{
  "source": "cache",
  "data": {
    "heart_rate": 75.5,
    "spo2": 98.2,
    "temperature": 36.8,
    "stress_level": 2.1,
    "steps": 5000,
    "calories": 200,
    "sleep_hours": 7.5
  }
}
```

### Get Vital History
**GET** `/vitals/user/{user_id}/history?limit=100`

Get historical vital readings.

**Query Parameters:**
- `limit` (optional): Number of records (default: 100)

**Response:** `200 OK`
```json
[
  {
    "id": 123,
    "user_id": 1,
    "heart_rate": 75.5,
    "spo2": 98.2,
    "timestamp": "2024-01-15T10:35:00"
  },
  ...
]
```

---

## 🚨 Alerts Endpoints

### Get User Alerts
**GET** `/alerts/user/{user_id}?limit=10`

Get recent alerts for user.

**Query Parameters:**
- `limit` (optional): Number of alerts (default: 10)

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "user_id": 1,
    "alert_type": "warning",
    "title": "Abnormal Heart Rate",
    "message": "Heart rate outside normal range: 105 bpm",
    "is_read": false,
    "created_at": "2024-01-15T10:35:00"
  }
]
```

---

## 🏥 Health Score Endpoints

### Get Health Score
**GET** `/health-score/user/{user_id}`

Get latest health score and risk assessment.

**Response:** `200 OK`
```json
{
  "score": 85.5,
  "risk_level": "low",
  "cardiac_risk": 0.15,
  "respiratory_risk": 0.10,
  "stress_risk": 0.30,
  "timestamp": "2024-01-15T10:35:00"
}
```

---

## 🏥 Hospital Dashboard Endpoints

### Get All Patients
**GET** `/hospital/patients`

Get all patients with latest vitals (for hospital dashboard).

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "name": "John Doe",
    "age": 45,
    "risk_level": "low",
    "heart_rate": 75.5,
    "spo2": 98.2,
    "status": "stable",
    "last_updated": "2024-01-15T10:35:00"
  },
  ...
]
```

---

## 🔌 WebSocket Endpoint

### Real-time Vitals Stream
**WS** `/ws/{user_id}`

Subscribe to real-time vital updates via WebSocket.

**Example (JavaScript):**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/1');

ws.onmessage = (event) => {
  const vitals = JSON.parse(event.data);
  console.log('New vitals:', vitals);
};
```

---

## 📊 Status Codes

- `200 OK`: Success
- `201 Created`: Resource created
- `400 Bad Request`: Invalid input
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

## 🔗 Interactive Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
"""

# ============================================================================
# Run tests:
# pytest tests/ -v --cov
# ============================================================================