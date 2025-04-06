# run_services.ps1
# Create necessary directories
if (-not (Test-Path -Path "logs")) {
    New-Item -ItemType Directory -Path "logs"
}
if (-not (Test-Path -Path "data")) {
    New-Item -ItemType Directory -Path "data"
}
if (-not (Test-Path -Path "metrics")) {
    New-Item -ItemType Directory -Path "metrics"
}

# Install required packages
if (-not (Test-Path -Path ".\.venv\Lib\site-packages\psutil")) {
    Write-Host "Installing required packages..."
    pip install psutil flask requests
}

# Initialize the database if needed
if (-not (Test-Path -Path "data\onfinance.db")) {
    Write-Host "Initializing database..."
    python scripts/init_db.py
}

# Start the frontend server
Write-Host "Starting frontend server..."
Start-Process python -ArgumentList "app/frontend/server.py" -WindowStyle Hidden

# Start the backend server
Write-Host "Starting backend server..."
Start-Process python -ArgumentList "app/backend/app.py" -WindowStyle Hidden

# Start the data integration pipeline
Write-Host "Starting data integration pipeline..."
Start-Process python -ArgumentList "scripts/data_integration.py" -WindowStyle Hidden

# Start the monitoring service
Write-Host "Starting monitoring service..."
Start-Process python -ArgumentList "scripts/monitoring.py" -WindowStyle Hidden

# Start the watchdog service
Write-Host "Starting watchdog service..."
Start-Process python -ArgumentList "watchdog.py" -WindowStyle Hidden

Write-Host "All services started. Use 'stop_services.ps1' to stop them."
