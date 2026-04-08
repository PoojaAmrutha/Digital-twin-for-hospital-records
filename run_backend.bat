@echo off
echo ====================================================
echo   Starting HealthWatch Backend (Local Environment)
echo ====================================================
echo.
echo Using Python at: .\venv\Scripts\python.exe
echo.

cd backend
.\venv\Scripts\python.exe -m uvicorn main:app --reload

if %errorlevel% neq 0 (
    echo.
    echo ❌ ERROR: Backend failed to start!
    echo    Please ensure you are in the 'd:\AIML\Digital-twin-for-hospital-records' folder
    echo    and that 'backend\venv' exists.
    pause
)
