---
description: Start the HealthWatch AI Backend Server
---

1. Open a terminal.
2. Navigate to the backend directory:
   ```powershell
   cd backend
   ```
3. (Optional) Create and activate a virtual environment:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate
   ```
4. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
5. Run the server using Uvicorn:
   ```powershell
   // turbo
   uvicorn main:app --reload
   ```
6. The API will be available at `http://127.0.0.1:8000`.
7. You can access the interactive documentation at `http://127.0.0.1:8000/docs`.
