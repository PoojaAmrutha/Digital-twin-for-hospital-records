import sys
import os
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from backend.database import SessionLocal
from backend.models import User, Alert
from backend.main import analyze_symptoms
from backend.schemas import SymptomAnalysisRequest

try:
    db = SessionLocal()
    
    # Needs a valid user ID (should be 2 based on previous run)
    user_id = 2 
    
    print(f"Testing symptom analysis for user {user_id}...")
    req = SymptomAnalysisRequest(
        user_id=user_id,
        symptoms="I have severe chest pain"
    )
    
    try:
        res = analyze_symptoms(request=req, db=db)
        print(f"✅ Success: {res}")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"❌ Error in analyze_symptoms: {e}")

except Exception as e:
    print(f"❌ Setup error: {e}")
finally:
    db.close()
