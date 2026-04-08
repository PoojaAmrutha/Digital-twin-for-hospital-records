"""
Definitive password fix - importing configuration directly from main.py
"""
import sys
import os

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)
os.chdir(backend_path)

from database import SessionLocal
from models import User
# IMPORT DIRECTLY FROM MAIN TO ENSURE EXACT MATCH
from main import pwd_context

def fix_password_definitively():
    session = SessionLocal()
    email = "lakshmi@hospital.com"
    password = "doctor123"
    
    try:
        print(f"🔍 Looking for user: {email}")
        user = session.query(User).filter(User.email == email).first()
        
        if not user:
            print("❌ User not found!")
            return

        print(f"✅ User found: {user.name}")
        
        # Hash using the IMPORTED context
        new_hash = pwd_context.hash(password)
        print(f"🔑 Generated new hash: {new_hash[:20]}...")
        
        # Verify immediately
        if pwd_context.verify(password, new_hash):
            print("✅ Verification check PASSED internally")
        else:
            print("❌ Verification check FAILED internally - this should not happen!")
            
        # Update DB
        user.password_hash = new_hash
        session.commit()
        print("💾 Database updated successfully")
        
        # Double check read back
        session.refresh(user)
        if pwd_context.verify(password, user.password_hash):
            print("🎉 Final DB verification: SUCCESS")
        else:
            print("💀 Final DB verification: FAILED")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    fix_password_definitively()
