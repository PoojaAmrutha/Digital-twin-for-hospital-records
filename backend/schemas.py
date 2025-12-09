# ============================================================================
# FILE: backend/schemas.py
# Pydantic Schemas for Request/Response Validation
# ============================================================================

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime


# ============================================================================
# USER SCHEMAS
# ============================================================================

class UserCreate(BaseModel):
    """Schema for creating a new user"""
    name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    age: int = Field(..., ge=0, le=150)
    gender: str = Field(..., pattern="^(M|F|Other)$")
    user_type: str = Field(default="patient", pattern="^(patient|doctor)$")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "john@example.com",
                "age": 45,
                "gender": "M",
                "user_type": "patient"
            }
        }


class UserResponse(BaseModel):
    """Schema for user response"""
    id: int
    name: str
    email: str
    age: int
    gender: str
    user_type: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """Schema for updating user information"""
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    age: Optional[int] = Field(None, ge=0, le=150)
    gender: Optional[str] = Field(None, pattern="^(M|F|Other)$")


# ============================================================================
# VITAL READING SCHEMAS
# ============================================================================

class VitalReadingCreate(BaseModel):
    """Schema for creating a vital reading"""
    user_id: int = Field(..., gt=0)
    heart_rate: float = Field(..., ge=20, le=250, description="Heart rate in bpm")
    spo2: float = Field(..., ge=0, le=100, description="Blood oxygen percentage")
    temperature: float = Field(..., ge=30, le=45, description="Body temperature in Celsius")
    stress_level: float = Field(..., ge=0, le=5, description="Stress level (0-5 scale)")
    steps: int = Field(default=0, ge=0, description="Daily steps count")
    calories: int = Field(default=0, ge=0, description="Calories burned")
    sleep_hours: float = Field(default=7.5, ge=0, le=24, description="Hours of sleep")
    
    @validator('spo2')
    def validate_spo2(cls, v):
        if v < 70:
            raise ValueError('SpO2 below 70% is life-threatening - please verify reading')
        return v
    
    @validator('heart_rate')
    def validate_heart_rate(cls, v):
        if v < 30 or v > 220:
            raise ValueError('Heart rate out of possible range - please verify reading')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "heart_rate": 75.5,
                "spo2": 98.2,
                "temperature": 36.8,
                "stress_level": 2.1,
                "steps": 5000,
                "calories": 200,
                "sleep_hours": 7.5
            }
        }


class VitalReadingResponse(VitalReadingCreate):
    """Schema for vital reading response"""
    id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True


class VitalReadingHistory(BaseModel):
    """Schema for historical vital readings"""
    heart_rate: float
    spo2: float
    temperature: float
    timestamp: datetime


# ============================================================================
# ALERT SCHEMAS
# ============================================================================

class AlertCreate(BaseModel):
    """Schema for creating an alert"""
    user_id: int
    alert_type: str = Field(..., pattern="^(warning|danger|critical)$")
    title: str = Field(..., min_length=3, max_length=255)
    message: str = Field(..., min_length=3, max_length=1000)


class AlertResponse(BaseModel):
    """Schema for alert response"""
    id: int
    user_id: int
    alert_type: str
    title: str
    message: str
    is_read: bool
    is_acknowledged: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class AlertUpdate(BaseModel):
    """Schema for updating alert status"""
    is_read: Optional[bool] = None
    is_acknowledged: Optional[bool] = None


# ============================================================================
# HEALTH SCORE SCHEMAS
# ============================================================================

class HealthScoreCreate(BaseModel):
    """Schema for creating health score"""
    user_id: int
    score: float = Field(..., ge=0, le=100)
    risk_level: str = Field(..., pattern="^(low|medium|high)$")
    cardiac_risk: float = Field(default=0.0, ge=0, le=1)
    respiratory_risk: float = Field(default=0.0, ge=0, le=1)
    stress_risk: float = Field(default=0.0, ge=0, le=1)


class HealthScoreResponse(BaseModel):
    """Schema for health score response"""
    score: float
    risk_level: str
    cardiac_risk: float
    respiratory_risk: float
    stress_risk: float
    timestamp: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class HealthScoreHistory(BaseModel):
    """Schema for health score history"""
    score: float
    risk_level: str
    timestamp: datetime


# ============================================================================
# PATIENT SUMMARY SCHEMAS
# ============================================================================

class PatientSummary(BaseModel):
    """Schema for patient summary (hospital dashboard)"""
    id: int
    name: str
    age: int
    gender: str
    risk_level: str
    heart_rate: Optional[float] = None
    spo2: Optional[float] = None
    temperature: Optional[float] = None
    status: str
    unread_alerts: int
    last_updated: Optional[datetime] = None


class PatientDetails(BaseModel):
    """Schema for detailed patient information"""
    patient: UserResponse
    latest_vitals: Optional[VitalReadingResponse] = None
    health_score: Optional[HealthScoreResponse] = None
    recent_alerts: list[AlertResponse] = []


# ============================================================================
# STATISTICS SCHEMAS
# ============================================================================

class SystemStats(BaseModel):
    """Schema for system-wide statistics"""
    total_patients: int
    total_vitals_recorded: int
    total_alerts: int
    critical_patients: int


# ============================================================================
# WEBSOCKET MESSAGE SCHEMAS
# ============================================================================

class WebSocketMessage(BaseModel):
    """Schema for WebSocket messages"""
    type: str  # 'vitals_update', 'alert', 'connection'
    user_id: int
    data: dict
    timestamp: datetime = Field(default_factory=datetime.utcnow)