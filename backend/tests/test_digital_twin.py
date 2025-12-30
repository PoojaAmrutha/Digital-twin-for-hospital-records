from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app, get_db
from database import Base
from models import User, MedicalRecord, AuditLog, EntityExtraction
import pytest
import os

# Setup test DB
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_dt.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(scope="module")
def setup_db():
    # Cleanup old db
    if os.path.exists("./test_dt.db"):
        os.remove("./test_dt.db")
        
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    # Create test users
    doctor = User(name="Dr. House", email="doctor@test.com", age=45, gender="M", user_type="doctor")
    patient = User(name="Patient Zero", email="patient@test.com", age=30, gender="F", user_type="patient")
    db.add(doctor)
    db.add(patient)
    db.commit()
    db.refresh(doctor)
    db.refresh(patient)
    
    yield {"db": db, "doctor_id": doctor.id, "patient_id": patient.id}
    
    db.close()
    if os.path.exists("./test_dt.db"):
        os.remove("./test_dt.db")

def test_create_medical_record(setup_db):
    ids = setup_db
    
    payload = {
        "record_type": "note",
        "content": "Patient shows signs of diabetes type 2. Prescribing Metformin.",
        "user_id": ids["patient_id"]
    }
    
    # We are simulating 'current_user_id' being passed or extracted (our modified main.py accepts it as param for simplicity?)
    # Wait, main.py definition: def create_medical_record(record: ..., current_user_id: int = 1, ...)
    # But it is not a query param because I didn't verify if I made it Query or Body. 
    # By default in FastAPI, simple types are Query params. So ?current_user_id=1 works.
    
    response = client.post(
        f"/medical-records/?current_user_id={ids['doctor_id']}",
        json=payload
    )
    
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["content"] == payload["content"]
    assert data["user_id"] == ids["patient_id"]
    
    # Check DB side
    db = ids["db"]
    record = db.query(MedicalRecord).filter(MedicalRecord.id == data["id"]).first()
    assert record is not None
    assert record.doctor_id == ids["doctor_id"]

def test_audit_log_creation(setup_db):
    ids = setup_db
    db = ids["db"]
    
    log = db.query(AuditLog).filter(AuditLog.target_table == "medical_records").first()
    assert log is not None
    assert log.action == "create"
    assert log.user_id == ids["doctor_id"]
    print("\n✅ Audit Log Verified")

def test_entity_extraction_mock(setup_db):
    # In main.py I added mock logic: if "diabetes" in content -> extract entity
    ids = setup_db
    db = ids["db"]
    
    # Get the record created in previous test
    record = db.query(MedicalRecord).first()
    
    # Check entities
    entities = db.query(EntityExtraction).filter(EntityExtraction.record_id == record.id).all()
    assert len(entities) > 0
    assert entities[0].entity_value == "Diabetes Type 2"
    print("\n✅ Entity Extraction Verified")

def test_get_digital_twin(setup_db):
    ids = setup_db
    
    response = client.get(f"/digital-twin/{ids['patient_id']}")
    assert response.status_code == 200
    data = response.json()
    
    assert data["user"]["id"] == ids["patient_id"]
    assert len(data["medical_records"]) >= 1
    assert "risks" in data
    print("\n✅ Digital Twin Retrieval Verified")
