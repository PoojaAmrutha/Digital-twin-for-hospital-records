import requests

url = "http://localhost:8000/prescriptions/upload"
file_path = "prescription.jpeg"
user_id = 1

try:
    with open(file_path, "rb") as f:
        files = {"file": f}
        data = {"user_id": user_id}
        print("Sending request...")
        response = requests.post(url, files=files, data=data)
        
    print(f"Status Code: {response.status_code}")
    print("Response JSON:")
    print(response.json())
except Exception as e:
    print(f"Error: {e}")
