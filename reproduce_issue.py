import requests
import json

API_URL = "http://127.0.0.1:8000"

def test_add_patient():
    import random
    new_patient = {
        "name": "Test Patient",
        "email": f"test.patient{random.randint(1000, 9999)}@example.com",
        "age": 30,
        "gender": "M",
        "user_type": "patient"
    }

    try:
        print(f"Sending POST request to {API_URL}/users/...")
        headers = {'Content-Type': 'application/json'}
        response = requests.post(f"{API_URL}/users/", json=new_patient)
        
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")
        
        if response.ok:
            print("Successfully created user.")
            user = response.json()
            print(f"User ID: {user['id']}")
            
            # Now try to add vitals (as per App.js logic)
            vitals_payload = {
                "user_id": user['id'],
                "heart_rate": 72,
                "spo2": 98,
                "temperature": 36.6,
                "stress_level": 2,
                "steps": 0,
                "calories": 0,
                "sleep_hours": 7.5
            }
            print(f"Sending POST request to {API_URL}/vitals/...")
            vitals_response = requests.post(f"{API_URL}/vitals/", json=vitals_payload)
            print(f"Vitals Response Status Code: {vitals_response.status_code}")
            print(f"Vitals Response Body: {vitals_response.text}")
            
        else:
            print("Failed to create user.")
            
    except Exception as e:
        print(f"Exception occurred: {e}")

if __name__ == "__main__":
    test_add_patient()
