import requests
import json

API_URL = "http://localhost:8000"

users = [
    {"name": "Dr. Venkat Rao", "email": "venkat@research.com", "age": 40, "gender": "M", "user_type": "researcher", "password": "admin123"},
    {"name": "Dr. Lakshmi Priya", "email": "lakshmi@hospital.com", "age": 35, "gender": "F", "user_type": "doctor", "password": "doctor123"},
    {"name": "Ananya Swami", "email": "ananya.demo@example.com", "age": 34, "gender": "F", "user_type": "patient", "password": "patient123"},
    {"name": "Legacy Patient", "email": "patient@healthwatch.ai", "age": 45, "gender": "M", "user_type": "patient", "password": "password123"}
]

print(f"Seeding {len(users)} users to {API_URL}...")

for user in users:
    try:
        response = requests.post(f"{API_URL}/users/", json=user)
        if response.status_code == 200:
            print(f"✅ Created: {user['name']} ({user['email']})")
        elif response.status_code == 400 and "Email already registered" in response.text:
            print(f"ℹ️  Exists:  {user['name']} ({user['email']})")
        else:
            print(f"❌ Failed:  {user['name']} - {response.status_code} {response.text}")
    except Exception as e:
        print(f"❌ Error:   {user['name']} - {str(e)}")

print("\nSeeding complete.")
