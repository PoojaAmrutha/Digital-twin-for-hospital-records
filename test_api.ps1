$ErrorActionPreference = "Stop"

Write-Host "1. Testing Connection to Backend (http://localhost:8000)..."
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/docs" -Method Head
    Write-Host "✅ Backend is ONLINE (Status code: $($response.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host "❌ Backend is OFFLINE or blocking connection." -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)"
    exit 1
}

Write-Host "`n2. Testing Login Endpoint..."
try {
    $body = @{
        username = "patient@healthwatch.ai"
        password = "password123"
    }
    $response = Invoke-RestMethod -Uri "http://localhost:8000/token" -Method Post -Body $body -ContentType "application/x-www-form-urlencoded"
    
    if ($response.access_token) {
        Write-Host "✅ Login SUCCESSFUL! Token received." -ForegroundColor Green
    } else {
        Write-Host "⚠️  Login failed (invalid credentials?)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Login Request Failed: $($_.Exception.Message)" -ForegroundColor Red
}
