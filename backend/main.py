# ============================================================================
# FILE: backend/main.py
# FastAPI Main Application
# ============================================================================

from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import asyncio
import json

from database import Base, engine, get_db
from models import User, VitalReading, Alert, HealthScore
from schemas import (
    UserCreate, UserResponse, 
    VitalReadingCreate, VitalReadingResponse,
    AlertResponse, HealthScoreResponse
)
from ml_models import anomaly_detector, health_calculator, risk_predictor
from alert_system import alert_system
from redis_client import redis_client

# Create FastAPI app
app = FastAPI(
    title="HealthWatch AI API",
    version="1.0.0",
    description="AI-Powered Health Monitoring System"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
Base.metadata.create_all(bind=engine)

# ============================================================================
# ROOT ENDPOINT
# ============================================================================

@app.get("/")
def read_root():
    """API health check"""
    return {
        "message": "HealthWatch AI API is running",
        "version": "1.0.0",
        "status": "healthy",
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "users": "/users/",
            "vitals": "/vitals/",
            "alerts": "/alerts/",
            "health_score": "/health-score/",
            "hospital": "/hospital/patients"
        }
    }


# ============================================================================
# USER ENDPOINTS
# ============================================================================

@app.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user (patient or doctor)"""
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user details by ID"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.get("/users/", response_model=List[UserResponse])
def get_all_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all users with pagination"""
    users = db.query(User).offset(skip).limit(limit).all()
    return users


# ============================================================================
# VITALS ENDPOINTS
# ============================================================================

@app.post("/vitals/", response_model=VitalReadingResponse)
def create_vital_reading(vital: VitalReadingCreate, db: Session = Depends(get_db)):
    """
    Create new vital reading and process it
    - Stores in PostgreSQL
    - Caches in Redis
    - Runs anomaly detection
    - Generates alerts if needed
    - Calculates health score
    """
    # Verify user exists
    user = db.query(User).filter(User.id == vital.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Store in database
    db_vital = VitalReading(**vital.dict())
    db.add(db_vital)
    db.commit()
    db.refresh(db_vital)
    
    # Cache in Redis for quick access
    vital_dict = vital.dict()
    redis_client.set_latest_vitals(vital.user_id, vital_dict)
    
    # Check for anomalies (if model is trained)
    try:
        is_anomaly = anomaly_detector.predict(vital_dict)
        if is_anomaly:
            anomaly_alert = {
                'type': 'warning',
                'title': 'Anomaly Detected',
                'message': 'Unusual vital pattern detected by AI',
                'timestamp': db_vital.timestamp.isoformat()
            }
            redis_client.add_alert(vital.user_id, anomaly_alert)
    except:
        pass  # Model might not be trained yet
    
    # Generate threshold-based alerts
    alerts = alert_system.check_vitals(vital_dict)
    
    # Store alerts in database and cache
    for alert_data in alerts:
        alert = Alert(
            user_id=vital.user_id,
            alert_type=alert_data['type'],
            title=alert_data['title'],
            message=alert_data['message']
        )
        db.add(alert)
        redis_client.add_alert(vital.user_id, alert_data)
    
    # Calculate health score and risks
    score_data = health_calculator.calculate(vital_dict)
    risks = risk_predictor.predict_risks(vital_dict)
    
    health_score = HealthScore(
        user_id=vital.user_id,
        score=score_data['score'],
        risk_level=score_data['risk_level'],
        cardiac_risk=risks['cardiac_risk'],
        respiratory_risk=risks['respiratory_risk'],
        stress_risk=risks['stress_risk']
    )
    db.add(health_score)
    
    db.commit()
    
    return db_vital


@app.get("/vitals/user/{user_id}/latest")
def get_latest_vitals(user_id: int, db: Session = Depends(get_db)):
    """Get latest vital reading for user (from cache or DB)"""
    # Try cache first for better performance
    cached = redis_client.get_latest_vitals(user_id)
    if cached:
        return {
            "source": "cache",
            "user_id": user_id,
            "data": cached
        }
    
    # Fall back to database
    vital = db.query(VitalReading).filter(
        VitalReading.user_id == user_id
    ).order_by(VitalReading.timestamp.desc()).first()
    
    if not vital:
        raise HTTPException(status_code=404, detail="No vitals found for this user")
    
    return {
        "source": "database",
        "user_id": user_id,
        "data": {
            "heart_rate": vital.heart_rate,
            "spo2": vital.spo2,
            "temperature": vital.temperature,
            "stress_level": vital.stress_level,
            "steps": vital.steps,
            "calories": vital.calories,
            "sleep_hours": vital.sleep_hours,
            "timestamp": vital.timestamp.isoformat()
        }
    }


@app.get("/vitals/user/{user_id}/history")
def get_vital_history(
    user_id: int,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get historical vital readings for user"""
    vitals = db.query(VitalReading).filter(
        VitalReading.user_id == user_id
    ).order_by(VitalReading.timestamp.desc()).limit(limit).all()
    
    if not vitals:
        raise HTTPException(status_code=404, detail="No vitals found for this user")
    
    return [
        {
            "id": v.id,
            "heart_rate": v.heart_rate,
            "spo2": v.spo2,
            "temperature": v.temperature,
            "stress_level": v.stress_level,
            "steps": v.steps,
            "calories": v.calories,
            "sleep_hours": v.sleep_hours,
            "timestamp": v.timestamp.isoformat()
        }
        for v in vitals
    ]


# ============================================================================
# ALERTS ENDPOINTS
# ============================================================================

@app.get("/alerts/user/{user_id}", response_model=List[AlertResponse])
def get_user_alerts(
    user_id: int,
    limit: int = 10,
    unread_only: bool = False,
    db: Session = Depends(get_db)
):
    """Get recent alerts for user"""
    # Try cache first
    cached_alerts = redis_client.get_alerts(user_id, limit)
    if cached_alerts and not unread_only:
        return cached_alerts
    
    # Query database
    query = db.query(Alert).filter(Alert.user_id == user_id)
    
    if unread_only:
        query = query.filter(Alert.is_read == False)
    
    alerts = query.order_by(Alert.created_at.desc()).limit(limit).all()
    
    return alerts


@app.put("/alerts/{alert_id}/mark-read")
def mark_alert_read(alert_id: int, db: Session = Depends(get_db)):
    """Mark an alert as read"""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.is_read = True
    db.commit()
    
    return {"message": "Alert marked as read", "alert_id": alert_id}


# ============================================================================
# HEALTH SCORE ENDPOINTS
# ============================================================================

@app.get("/health-score/user/{user_id}")
def get_health_score(user_id: int, db: Session = Depends(get_db)):
    """Get latest health score and risk assessment for user"""
    score = db.query(HealthScore).filter(
        HealthScore.user_id == user_id
    ).order_by(HealthScore.timestamp.desc()).first()
    
    if not score:
        raise HTTPException(status_code=404, detail="No health score found for this user")
    
    return {
        "user_id": user_id,
        "score": score.score,
        "risk_level": score.risk_level,
        "cardiac_risk": score.cardiac_risk,
        "respiratory_risk": score.respiratory_risk,
        "stress_risk": score.stress_risk,
        "timestamp": score.timestamp.isoformat()
    }


@app.get("/health-score/user/{user_id}/history")
def get_health_score_history(
    user_id: int,
    limit: int = 30,
    db: Session = Depends(get_db)
):
    """Get historical health scores for trend analysis"""
    scores = db.query(HealthScore).filter(
        HealthScore.user_id == user_id
    ).order_by(HealthScore.timestamp.desc()).limit(limit).all()
    
    if not scores:
        raise HTTPException(status_code=404, detail="No health scores found")
    
    return [
        {
            "score": s.score,
            "risk_level": s.risk_level,
            "timestamp": s.timestamp.isoformat()
        }
        for s in scores
    ]


# ============================================================================
# HOSPITAL DASHBOARD ENDPOINTS
# ============================================================================

@app.get("/hospital/patients")
def get_all_patients(db: Session = Depends(get_db)):
    """Get all patients with their latest vitals and status (for hospital dashboard)"""
    patients = db.query(User).filter(User.user_type == "patient").all()
    
    result = []
    for patient in patients:
        # Get latest vitals
        latest_vital = db.query(VitalReading).filter(
            VitalReading.user_id == patient.id
        ).order_by(VitalReading.timestamp.desc()).first()
        
        # Get latest health score
        latest_score = db.query(HealthScore).filter(
            HealthScore.user_id == patient.id
        ).order_by(HealthScore.timestamp.desc()).first()
        
        # Get unread alerts count
        unread_alerts = db.query(Alert).filter(
            Alert.user_id == patient.id,
            Alert.is_read == False
        ).count()
        
        # Determine status based on vitals
        status = "stable"
        if latest_vital:
            if latest_vital.heart_rate > 130 or latest_vital.heart_rate < 40 or latest_vital.spo2 < 88:
                status = "critical"
            elif latest_vital.heart_rate > 100 or latest_vital.spo2 < 92 or latest_vital.temperature > 38.5:
                status = "warning"
        
        result.append({
            "id": patient.id,
            "name": patient.name,
            "age": patient.age,
            "gender": patient.gender,
            "risk_level": latest_score.risk_level if latest_score else "unknown",
            "heart_rate": round(latest_vital.heart_rate, 1) if latest_vital else None,
            "spo2": round(latest_vital.spo2, 1) if latest_vital else None,
            "temperature": round(latest_vital.temperature, 1) if latest_vital else None,
            "status": status,
            "unread_alerts": unread_alerts,
            "last_updated": latest_vital.timestamp.isoformat() if latest_vital else None
        })
    
    # Sort by status priority (critical first)
    status_priority = {"critical": 0, "warning": 1, "stable": 2}
    result.sort(key=lambda x: status_priority.get(x["status"], 3))
    
    return result


@app.get("/hospital/patient/{user_id}/details")
def get_patient_details(user_id: int, db: Session = Depends(get_db)):
    """Get detailed information for a specific patient"""
    patient = db.query(User).filter(User.id == user_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Get latest vitals
    latest_vital = db.query(VitalReading).filter(
        VitalReading.user_id == user_id
    ).order_by(VitalReading.timestamp.desc()).first()
    
    # Get latest health score
    latest_score = db.query(HealthScore).filter(
        HealthScore.user_id == user_id
    ).order_by(HealthScore.timestamp.desc()).first()
    
    # Get recent alerts
    recent_alerts = db.query(Alert).filter(
        Alert.user_id == user_id
    ).order_by(Alert.created_at.desc()).limit(5).all()
    
    return {
        "patient": {
            "id": patient.id,
            "name": patient.name,
            "age": patient.age,
            "gender": patient.gender,
            "email": patient.email
        },
        "latest_vitals": {
            "heart_rate": latest_vital.heart_rate,
            "spo2": latest_vital.spo2,
            "temperature": latest_vital.temperature,
            "stress_level": latest_vital.stress_level,
            "steps": latest_vital.steps,
            "calories": latest_vital.calories,
            "sleep_hours": latest_vital.sleep_hours,
            "timestamp": latest_vital.timestamp.isoformat()
        } if latest_vital else None,
        "health_score": {
            "score": latest_score.score,
            "risk_level": latest_score.risk_level,
            "cardiac_risk": latest_score.cardiac_risk,
            "respiratory_risk": latest_score.respiratory_risk,
            "stress_risk": latest_score.stress_risk
        } if latest_score else None,
        "recent_alerts": [
            {
                "title": alert.title,
                "message": alert.message,
                "type": alert.alert_type,
                "timestamp": alert.created_at.isoformat()
            }
            for alert in recent_alerts
        ]
    }


# ============================================================================
# WEBSOCKET ENDPOINT
# ============================================================================

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    """WebSocket for real-time vital updates"""
    await websocket.accept()
    try:
        while True:
            # Get latest vitals from Redis
            vitals = redis_client.get_latest_vitals(user_id)
            if vitals:
                await websocket.send_json({
                    "type": "vitals_update",
                    "user_id": user_id,
                    "data": vitals
                })
            await asyncio.sleep(1)  # Send updates every second
    except WebSocketDisconnect:
        print(f"WebSocket disconnected for user {user_id}")
    except Exception as e:
        print(f"WebSocket error: {e}")


# ============================================================================
# STATISTICS ENDPOINTS
# ============================================================================

@app.get("/stats/overview")
def get_system_overview(db: Session = Depends(get_db)):
    """Get system-wide statistics"""
    total_patients = db.query(User).filter(User.user_type == "patient").count()
    total_vitals = db.query(VitalReading).count()
    total_alerts = db.query(Alert).count()
    
    # Critical patients
    critical_patients = db.query(User).join(VitalReading).filter(
        VitalReading.heart_rate > 130,
        User.user_type == "patient"
    ).distinct().count()
    
    return {
        "total_patients": total_patients,
        "total_vitals_recorded": total_vitals,
        "total_alerts": total_alerts,
        "critical_patients": critical_patients
    }


# ============================================================================
# Run with: uvicorn main:app --reload --host 0.0.0.0 --port 8000
# ============================================================================