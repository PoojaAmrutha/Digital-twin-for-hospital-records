
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
    password_hash = Column(String(255), nullable=True) # Check note below regarding migration
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


class MedicalRecord(Base):
    """
    Medical Record model - stores unstructured text data
    """
    __tablename__ = "medical_records"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=True) # Creator
    
    record_type = Column(String(50), nullable=False) # 'note', 'lab_report', 'imaging', 'discharge_summary'
    content = Column(Text, nullable=False) # Unstructured text
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    version = Column(Integer, default=1)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], backref="medical_records")
    doctor = relationship("User", foreign_keys=[doctor_id])
    entities = relationship("EntityExtraction", back_populates="record", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<MedicalRecord(id={self.id}, type='{self.record_type}', user_id={self.user_id})>"


class EntityExtraction(Base):
    """
    Entity Extraction model - stores structured entities extracted from medical records by LLM
    """
    __tablename__ = "entity_extractions"
    
    id = Column(Integer, primary_key=True, index=True)
    record_id = Column(Integer, ForeignKey("medical_records.id"), nullable=False, index=True)
    
    entity_type = Column(String(50), nullable=False) # 'diagnosis', 'medication', 'symptom'
    entity_value = Column(String(255), nullable=False)
    confidence_score = Column(Float, nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    record = relationship("MedicalRecord", back_populates="entities")

    def __repr__(self):
        return f"<Entity(type='{self.entity_type}', value='{self.entity_value}')>"


class AuditLog(Base):
    """
    Audit Log model - tracks all data changes for compliance
    """
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True) # Who made the change
    target_id = Column(Integer, nullable=True) # ID of the modified record
    target_table = Column(String(50), nullable=False) # Table name
    
    action = Column(String(20), nullable=False) # 'create', 'update', 'delete'
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationship
    user = relationship("User")

    def __repr__(self):
        return f"<AuditLog(action='{self.action}', table='{self.target_table}', user_id={self.user_id})>"
