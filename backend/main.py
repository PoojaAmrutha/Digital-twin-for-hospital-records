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
from models import User, VitalReading, Alert, HealthScore, MedicalRecord, EntityExtraction, AuditLog
from schemas import (
    UserCreate, UserResponse, UserUpdate,
    VitalReadingCreate, VitalReadingResponse, VitalReadingUpdate,
    AlertResponse, HealthScoreResponse,
    MedicalRecordCreate, MedicalRecordResponse, DigitalTwinResponse,
    SymptomAnalysisRequest, SymptomAnalysisResponse, UserLogin
)

from ml_models import anomaly_detector, health_calculator, risk_predictor, readmission_model, treatment_model
from alert_system import alert_system
from redis_client import redis_client
from llm_service import llm_service
from auditing import audit_logger
from passlib.context import CryptContext

# Password hashing context
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")



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
    
    db_user = User(
        name=user.name,
        email=user.email,
        age=user.age,
        gender=user.gender,
        user_type=user.user_type,
        password_hash=pwd_context.hash(user.password)
    )
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


@app.post("/auth/login", response_model=UserResponse)
def login(user_login: UserLogin, db: Session = Depends(get_db)):
    """Authenticate user and return details"""
    user = db.query(User).filter(User.email == user_login.email).first()
    if not user or not user.password_hash or not pwd_context.verify(user_login.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    return user



@app.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    """Update user information"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update only provided fields
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    return user


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


@app.put("/vitals/user/{user_id}/update", response_model=VitalReadingResponse)
def update_patient_vitals(
    user_id: int,
    vital_update: VitalReadingUpdate,
    db: Session = Depends(get_db)
):
    """
    Update patient vitals (Doctor Only)
    Allows doctors to manually input/update vital signs
    """
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get latest vitals or create new
    latest_vital = db.query(VitalReading).filter(
        VitalReading.user_id == user_id
    ).order_by(VitalReading.timestamp.desc()).first()
    
    # Prepare update data
    update_data = vital_update.dict(exclude_unset=True)
    
    if latest_vital and update_data:
        # Update existing vitals
        for field, value in update_data.items():
            setattr(latest_vital, field, value)
        db.commit()
        db.refresh(latest_vital)
        return latest_vital
    else:
        # Create new vital reading with updated values
        base_vitals = {
            "user_id": user_id,
            "heart_rate": 75,
            "spo2": 96,
            "temperature": 36.8,
            "stress_level": 3,
            "steps": 0,
            "calories": 0,
            "sleep_hours": 7.5
        }
        base_vitals.update(update_data)
        
        new_vital = VitalReading(**base_vitals)
        db.add(new_vital)
        db.commit()
        db.refresh(new_vital)
        return new_vital


@app.post("/symptoms/analyze", response_model=SymptomAnalysisResponse)
def analyze_symptoms(
    request: SymptomAnalysisRequest,
    db: Session = Depends(get_db)
):
    """
    Analyze patient symptoms and suggest vital adjustments
    Used by patient chatbot to automatically adjust vitals based on symptoms
    """
    symptoms_text = request.symptoms.lower()

    detected_symptoms = []
    suggested_vitals = {}
    severity = "mild"
    
    # Keyword-based symptom detection and vital adjustment
    # Fever symptoms
    if any(word in symptoms_text for word in ['fever', 'hot', 'burning', 'temperature', 'feverish']):
        detected_symptoms.append('fever')
        suggested_vitals['temperature'] = 38.5
        severity = "moderate"
    
    # Respiratory symptoms
    if any(word in symptoms_text for word in ['breathe', 'breathing', 'breath', 'shortness', 'wheez', 'cough']):
        detected_symptoms.append('respiratory_distress')
        suggested_vitals['spo2'] = 92
        suggested_vitals['respiratoryRate'] = 24
        severity = "moderate"
    
    # Cardiac symptoms
    if any(word in symptoms_text for word in ['chest pain', 'heart', 'palpitation', 'racing']):
        detected_symptoms.append('cardiac_symptoms')
        suggested_vitals['heart_rate'] = 105
        suggested_vitals['stress_level'] = 4.0
        severity = "severe"
    
    # Anxiety/stress symptoms
    if any(word in symptoms_text for word in ['anxious', 'anxiety', 'stress', 'worried', 'panic', 'nervous']):
        detected_symptoms.append('anxiety')
        suggested_vitals['stress_level'] = 4.5
        suggested_vitals['heart_rate'] = 95
        severity = "moderate"
    
    # Pain symptoms
    if any(word in symptoms_text for word in ['pain', 'ache', 'hurt', 'sore']):
        detected_symptoms.append('pain')
        suggested_vitals['stress_level'] = 3.5
        if 'severe' in symptoms_text or 'extreme' in symptoms_text:
            severity = "severe"
            
            # Create CRITICAL ALERT for doctor
            alert_msg = f"Patient {request.user_id} reported SEVERE symptoms: {request.symptoms}. Immediate attention recommended."
            critical_alert = Alert(
                user_id=request.user_id,
                alert_type="critical",
                title="Critical Symptom Reported",
                message=alert_msg,
                created_at=datetime.utcnow(),
                is_read=False
            )
            db.add(critical_alert)
            db.commit()
            
            # Also notify via Redis for real-time dashboards
            redis_client.add_alert(request.user_id, {
                "type": "critical",
                "title": "Critical Symptom Reported",
                "message": alert_msg,
                "timestamp": datetime.utcnow().isoformat()
            })

    
    # Headache
    if any(word in symptoms_text for word in ['headache', 'migraine']):
        detected_symptoms.append('headache')
        suggested_vitals['stress_level'] = 3.0
    
    # Fatigue
    if any(word in symptoms_text for word in ['tired', 'fatigue', 'exhausted', 'weak']):
        detected_symptoms.append('fatigue')
        suggested_vitals['steps'] = 500
        suggested_vitals['sleep_hours'] = 5.0
    
    # Dizziness
    if any(word in symptoms_text for word in ['dizzy', 'lightheaded', 'faint']):
        detected_symptoms.append('dizziness')
        suggested_vitals['spo2'] = 93
        severity = "moderate"
    
    # If no specific symptoms detected, use mild defaults
    if not detected_symptoms:
        detected_symptoms = ['general_discomfort']
        suggested_vitals = {
            'stress_level': 2.5
        }
    
    # Generate response message
    if severity == "severe":
        message = "⚠️ Your symptoms suggest a serious condition. Please seek immediate medical attention. I've updated your vitals to reflect this."
    elif severity == "moderate":
        message = "Your symptoms have been noted. I recommend consulting with your doctor soon. Your vitals have been adjusted."
    else:
        message = "I've recorded your symptoms. Your vitals have been updated. Monitor your condition and contact your doctor if symptoms worsen."
    
    # Update patient vitals in database
    try:
        # 1. Update Vitals
        latest_vital = db.query(VitalReading).filter(
            VitalReading.user_id == request.user_id
        ).order_by(VitalReading.timestamp.desc()).first()
        
        if latest_vital:
            for field, value in suggested_vitals.items():
                if hasattr(latest_vital, field):
                    setattr(latest_vital, field, value)
            db.commit()
        else:
            # Create new vital reading
            base_vitals = {
                "user_id": request.user_id,
                "heart_rate": 75,
                "spo2": 96,
                "temperature": 36.8,
                "stress_level": 3,
                "steps": 0,
                "calories": 0,
                "sleep_hours": 7.5
            }
            base_vitals.update(suggested_vitals)
            new_vital = VitalReading(**base_vitals)
            db.add(new_vital)
            db.commit()

        # 2. Store Symptoms as a Medical Record
        new_record = MedicalRecord(
            user_id=request.user_id,
            record_type="symptom_log",
            content=f"Patient described symptoms through chatbot: {request.symptoms}. AI matched: {', '.join(detected_symptoms)}. Severity: {severity}."
        )
        db.add(new_record)
        db.commit()

    except Exception as e:
        print(f"Error updating vitals/records: {e}")
    
    return SymptomAnalysisResponse(
        detected_symptoms=detected_symptoms,
        suggested_vitals=suggested_vitals,
        message=message,
        severity=severity
    )


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
# DIGITAL TWIN ENDPOINTS
# ============================================================================

@app.post("/medical-records/", response_model=MedicalRecordResponse)
def create_medical_record(
    record: MedicalRecordCreate, 
    current_user_id: int = 1, # Placeholder: In real app, extract from JWT
    db: Session = Depends(get_db)
):
    """
    Create a new medical record (Doctor Only)
    Triggers LLM extraction and Audit Logging
    """
    # 1. RBAC Check (Mocked for now)
    # Check if current_user_id is a doctor
    # doctor = db.query(User).filter(User.id == current_user_id).first()
    # if not doctor or doctor.user_type != "doctor": ...
    
    # 2. Create Record
    db_record = MedicalRecord(**record.dict())
    db_record.doctor_id = current_user_id
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    
    # 3. Audit Log
    audit_logger.log_change(
        db, 
        user_id=current_user_id, 
        target_table="medical_records", 
        target_id=db_record.id, 
        action="create", 
        new_value=record.dict()
    )
    
    # 4. LLM Entity Extraction
    # Run in background in real app
    try:
        entities = llm_service.extract_entities(record.content)
        # Mocking entities if service returns empty (since it's a skeleton)
        if not entities and "diabetes" in record.content.lower():
            entities = [{"type": "diagnosis", "value": "Diabetes Type 2", "confidence": 0.95}]
            
        for ent in entities:
            db_entity = EntityExtraction(
                record_id=db_record.id,
                entity_type=ent.get('type', 'unknown'),
                entity_value=ent.get('value', 'unknown'),
                confidence_score=ent.get('confidence', 0.0)
            )
            db.add(db_entity)
        db.commit()
    except Exception as e:
        print(f"Entity extraction error: {e}")
        
    db.refresh(db_record)
    return db_record

@app.get("/digital-twin/{user_id}", response_model=DigitalTwinResponse)
def get_digital_twin(user_id: int, db: Session = Depends(get_db)):
    """
    Get the full Digital Twin representation
    Aggregates Profile, Vitals, History, Risks
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    latest_vital = db.query(VitalReading).filter(
        VitalReading.user_id == user_id
    ).order_by(VitalReading.timestamp.desc()).first()
    
    records = db.query(MedicalRecord).filter(
        MedicalRecord.user_id == user_id
    ).order_by(MedicalRecord.created_at.desc()).all()
    
    # Run Risk Models
    risk_data = {
        "age": user.age,
        "recent_admissions": len(records) # simplistic proxy
    }
    readmission_risk = readmission_model.predict(risk_data)
    
    return {
        "user": user,
        "latest_vitals": latest_vital,
        "metrics": {
            "bmi": 24.5, # Placeholder calculation
            "last_visit": records[0].created_at if records else None
        },
        "medical_records": records,
        "risks": readmission_risk
    }

# ============================================================================
# Run with: uvicorn main:app --reload --host 0.0.0.0 --port 8000
# ============================================================================