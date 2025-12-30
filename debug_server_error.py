import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from backend.database import SessionLocal, init_db
from backend.models import User
from backend.main import create_user
from backend.schemas import UserCreate
from pydantic import ValidationError

try:
    db = SessionLocal()
    # Init DB just in case
    init_db()
    
    print("Attempting to create user directly...")
    user_in = UserCreate(
        name="Debug User",
        email="debug@example.com",
        age=30,
        gender="M",
        user_type="patient",
        password="debugpassword"
    )
    
    print(f"User in: {user_in}")
    
    # Simulate DB session dependency
    try:
        created_user = create_user(user=user_in, db=db)
        print(f"✅ Success! User created: {created_user.id}")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"❌ Error in create_user: {e}")
        
except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"❌ Script setup error: {e}")
finally:
    db.close()
