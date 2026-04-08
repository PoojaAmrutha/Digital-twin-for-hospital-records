
import requests
import json

url = "http://localhost:8000/auth/login"
payload = {
    "email": "test@example.com",
    "password": "password123"
}

try:
    print(f"Sending POST request to {url}")
    response = requests.post(url, json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
