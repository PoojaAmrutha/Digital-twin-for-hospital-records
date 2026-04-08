"""
Reset password for Dr. Lakshmi Priya
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

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def reset_doctor_password():
    """Reset Dr. Lakshmi Priya's password to 'doctor123'"""
    session = SessionLocal()
    
    try:
        # Find the doctor
        doctor = session.query(User).filter(
            User.email == "lakshmi@hospital.com"
        ).first()
        
        if doctor:
            # Hash the password
            new_password = "doctor123"
            hashed_password = pwd_context.hash(new_password)
            doctor.password_hash = hashed_password
            
            session.commit()
            
            print("=" * 60)
            print("✅ Password reset successful!")
            print("=" * 60)
            print(f"Name: {doctor.name}")
            print(f"Email: {doctor.email}")
            print(f"Password: {new_password}")
            print(f"User Type: {doctor.user_type}")
            print("=" * 60)
        else:
            print("❌ Doctor account not found!")
            print("Looking for: lakshmi@hospital.com")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    reset_doctor_password()
