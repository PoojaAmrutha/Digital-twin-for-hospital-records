import requests
import random
import sys

API_URL = "http://127.0.0.1:8000"

def seed_multiple_patients():
    print("🌱 Seeding database with historical patient data...")
    
    patients = [
        {"name": "Sarah Connor", "age": 35, "gender": "F"},
        {"name": "Bruce Wayne", "age": 42, "gender": "M"},
        {"name": "Clark Kent", "age": 38, "gender": "M"},
        {"name": "Diana Prince", "age": 300, "gender": "F"},
        {"name": "Peter Parker", "age": 22, "gender": "M"},
        {"name": "Wanda Maximoff", "age": 29, "gender": "F"},
        {"name": "Steve Rogers", "age": 100, "gender": "M"},
        {"name": "Natasha Romanoff", "age": 34, "gender": "F"}
    ]

    created_count = 0
    
    for p in patients:
        email = f"{p['name'].lower().replace(' ', '.')}@healthwatch.ai"
        password = "password123"
        
        payload = {
            "name": p['name'],
            "email": email,
            "age": p['age'],
            "gender": p['gender'],
            "user_type": "patient",
            "password": password
        }
        
        try:
            res = requests.post(f"{API_URL}/users/", json=payload)
            if res.status_code == 200:
                print(f"✅ Created: {p['name']} ({email})")
                created_count += 1
                
                # Create initial vitals for them
                user_id = res.json()['id']
                vitals = {
                    "user_id": user_id,
                    "heart_rate": random.randint(60, 90),
                    "spo2": random.randint(95, 100),
                    "temperature": round(random.uniform(36.1, 37.2), 1),
                    "stress_level": random.randint(1, 5),
                    "steps": random.randint(2000, 10000),
                    "calories": random.randint(1500, 2500),
                    "sleep_hours": round(random.uniform(6.0, 9.0), 1)
                }
                requests.post(f"{API_URL}/vitals/", json=vitals)
                
            elif res.status_code == 400:
                print(f"ℹ️ Exists: {p['name']}")
            else:
                print(f"❌ Failed {p['name']}: {res.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            
    print(f"\n✨ Seeded {created_count} new patients.")

if __name__ == "__main__":
    seed_multiple_patients()
