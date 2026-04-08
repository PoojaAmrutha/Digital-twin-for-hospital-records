"""
Fix password hash for Dr. Lakshmi Priya using the correct algorithm (pbkdf2_sha256)
to match backend/main.py configuration and avoid bcrypt dependency issues.
"""
import sys
import os

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)
os.chdir(backend_path)

from database import SessionLocal
from models import User
from passlib.context import CryptContext

# MATCHING backend/main.py configuration exactly
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def fix_doctor_password():
    """Reset Dr. Lakshmi Priya's password to 'doctor123' using pbkdf2_sha256"""
    session = SessionLocal()
    
    try:
        # Find the doctor
        doctor = session.query(User).filter(
            User.email == "lakshmi@hospital.com"
        ).first()
        
        if doctor:
            # Hash the password using PBKDF2
            new_password = "doctor123"
            hashed_password = pwd_context.hash(new_password)
            doctor.password_hash = hashed_password
            
            session.commit()
            
            print("=" * 60)
            print("✅ Password hash fixed!")
            print("=" * 60)
            print(f"Name: {doctor.name}")
            print(f"Email: {doctor.email}")
            print(f"Password: {new_password}")
            print(f"Algorithm: pbkdf2_sha256")
            print("=" * 60)
        else:
            print("❌ Doctor account not found!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    fix_doctor_password()
