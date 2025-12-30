import requests
import sys

API_URL = "http://127.0.0.1:8000"

def seed_users():
    print("🌱 Seeding database with default users...")
    
    # 1. Create Doctor
    doctor = {
        "name": "Dr. House",
        "email": "doctor@healthwatch.ai",
        "age": 50,
        "gender": "M",
        "user_type": "doctor",
        "password": "password123"
    }
    
    try:
        res = requests.post(f"{API_URL}/users/", json=doctor)
        if res.status_code == 200:
            print(f"✅ Created Doctor: {doctor['email']} / password123")
        elif res.status_code == 400:
            print(f"ℹ️ Doctor already exists: {doctor['email']}")
        else:
            print(f"❌ Failed to create doctor: {res.text}")
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return

    # 2. Create Patient
    patient = {
        "name": "John Doe",
        "email": "patient@healthwatch.ai",
        "age": 30,
        "gender": "M",
        "user_type": "patient",
        "password": "password123"
    }
    
    try:
        res = requests.post(f"{API_URL}/users/", json=patient)
        if res.status_code == 200:
            print(f"✅ Created Patient: {patient['email']} / password123")
        elif res.status_code == 400:
            print(f"ℹ️ Patient already exists: {patient['email']}")
        else:
            print(f"❌ Failed to create patient: {res.text}")

    except Exception as e:
        print(f"❌ Connection error: {e}")

if __name__ == "__main__":
    seed_users()
