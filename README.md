# HealthWatch AI - Manual Setup Guide

This guide explains how to run the HealthWatch AI system locally on Windows.

## Prerequisites

Ensure you have the following installed:
- **Python 3.8+**
- **Node.js 16+** & **npm**

## 1. Backend Setup

The backend powers the API, database, and AI models.

### Step 1: Open a Terminal
Open your terminal (PowerShell or Command Prompt) and navigate to the `backend` directory:
```powershell
cd backend
```

### Step 2: Create a Virtual Environment
Isolate your Python dependencies by creating a virtual environment:
```powershell
python -m venv venv
```

### Step 3: Activate the Environment
- **Windows (PowerShell):**
  ```powershell
  .\venv\Scripts\Activate
  ```
- **Windows (Command Prompt):**
  ```cmd
  venv\Scripts\activate.bat
  ```

### Step 4: Install Dependencies
Install the required libraries:
```powershell
pip install -r requirements.txt
```

### Step 5: Initialize the Database
The system uses SQLite by default (so no PostgreSQL installation is needed). Run this command to create the database tables:
```powershell
python run_simulation.py --mode init
```

### Step 6: Start the Backend Server
Launch the server. It will run on `http://localhost:8000`.
```powershell
uvicorn main:app --reload
```

> **Note on Redis:** You may see a generic warning like `⚠️ Redis connection failed`. This is expected if you don't have Redis installed. The system will automatically run in "no-cache" mode, which is perfectly fine for local testing.

---

## 2. Frontend Setup

The frontend provides the user dashboard. Open a **new** terminal window (keep the backend running!).

### Step 1: Navigate to Frontend
```powershell
cd frontend
```

### Step 2: Install Dependencies
Download the web dependencies:
```powershell
npm install
```

### Step 3: Configure Environment
Create a file named `.env` in the `frontend` folder (if it doesn't await exist) and add this line to tell the frontend where the backend is:
```text
REACT_APP_API_URL=http://localhost:8000
```

### Step 4: Start the Frontend
Launch the user interface:

```powershell
npm start
```

Result: The application should automatically open in your browser at `http://localhost:3000`.

---

## 3. Running Simulations (Optional)

To see dynamic data on your dashboard, you can simulate a patient's vitals.
Open a third terminal, activate the backend virtual environment again, and run:

```powershell
cd backend
.\venv\Scripts\Activate
python run_simulation.py --mode simulate --user_id 1 --duration 120
```
This sends fake heart rate and SPO2 data for 120 seconds.
