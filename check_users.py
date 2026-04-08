"""
Check current user credentials in the database
"""
import sys
import os

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)
os.chdir(backend_path)

from database import SessionLocal
from models import User

def check_users():
    """Display all users and their credentials"""
    session = SessionLocal()
    
    try:
        print("=" * 80)
        print("CURRENT USER ACCOUNTS")
        print("=" * 80)
        print()
        
        users = session.query(User).all()
        
        for user in users:
            print(f"Name: {user.name:30} | Email: {user.email:35} | Type: {user.user_type}")
        
        print()
        print("=" * 80)
        print(f"Total users: {len(users)}")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    check_users()
