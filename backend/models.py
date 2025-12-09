
# FILE: backend/models.py

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class User(Base):
    """
    User model - represents patients and doctors
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    age = Column(Integer)
    gender = Column(String(10))
    user_type = Column(String(50), default="patient")  # 'patient' or 'doctor'
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    vitals = relationship("VitalReading", back_populates="user", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="user", cascade="all, delete-orphan")
    health_scores = relationship("HealthScore", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}', type='{self.user_type}')>"


class VitalReading(Base):
    """
    Vital Reading model - stores all vital measurements
    """
    __tablename__ = "vital_readings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Vital measurements
    heart_rate = Column(Float, nullable=False)          # beats per minute
    spo2 = Column(Float, nullable=False)                # blood oxygen percentage
    temperature = Column(Float, nullable=False)         # celsius
    stress_level = Column(Float, nullable=False)        # 0-5 scale
    
    # Activity data
    steps = Column(Integer, default=0)                  # daily steps
    calories = Column(Integer, default=0)               # calories burned
    sleep_hours = Column(Float, default=0.0)            # hours of sleep
    
    # Metadata
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationship
    user = relationship("User", back_populates="vitals")
    
    def __repr__(self):
        return f"<VitalReading(id={self.id}, user_id={self.user_id}, hr={self.heart_rate}, timestamp={self.timestamp})>"


class Alert(Base):
    """
    Alert model - stores health alerts and warnings
    """
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Alert details
    alert_type = Column(String(50), nullable=False)     # 'warning', 'danger', 'critical'
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    
    # Status
    is_read = Column(Boolean, default=False)
    is_acknowledged = Column(Boolean, default=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    acknowledged_at = Column(DateTime, nullable=True)
    
    # Relationship
    user = relationship("User", back_populates="alerts")
    
    def __repr__(self):
        return f"<Alert(id={self.id}, user_id={self.user_id}, type='{self.alert_type}', title='{self.title}')>"


class HealthScore(Base):
    """
    Health Score model - stores calculated health scores and risk assessments
    """
    __tablename__ = "health_scores"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Overall score
    score = Column(Float, nullable=False)               # 0-100 scale
    risk_level = Column(String(50), nullable=False)     # 'low', 'medium', 'high'
    
    # Detailed risk scores (0-1 scale)
    cardiac_risk = Column(Float, default=0.0)
    respiratory_risk = Column(Float, default=0.0)
    stress_risk = Column(Float, default=0.0)
    
    # Additional metrics
    trend = Column(String(20), nullable=True)           # 'improving', 'stable', 'declining'
    
    # Metadata
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationship
    user = relationship("User", back_populates="health_scores")
    
    def __repr__(self):
        return f"<HealthScore(id={self.id}, user_id={self.user_id}, score={self.score}, risk='{self.risk_level}')>"


class DoctorPatientAssignment(Base):
    """
    Doctor-Patient Assignment model - links doctors to their patients
    """
    __tablename__ = "doctor_patient_assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Assignment details
    assigned_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<Assignment(doctor_id={self.doctor_id}, patient_id={self.patient_id})>"