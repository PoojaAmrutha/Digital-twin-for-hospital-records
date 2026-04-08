
import sys
import os
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import User

# Add parent directory to path to handle imports if run from backend subdir
sys.path.append(os.getcwd())

def test_query():
    db = SessionLocal()
    try:
        print("Attempting to query User table...")
        user = db.query(User).first()
        print("Query successful.")
        if user:
            print(f"Found user: {user.email}")
        else:
            print("No users found.")
    except Exception as e:
        print("An error occurred:")
        print(e)
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_query()
