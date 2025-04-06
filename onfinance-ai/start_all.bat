@echo off
echo Starting OnFinance AI services...

:: Create necessary directories
mkdir logs 2>nul
mkdir data 2>nul

:: Activate virtual environment
call .venv\Scripts\activate.bat

:: Initialize database
echo Initializing database...
python scripts/init_db.py

:: Start backend (in a new window)
echo Starting backend service...
start cmd /k "title OnFinance Backend && .venv\Scripts\activate.bat && python app/backend/app.py"

:: Give backend time to start
timeout /t 3 /nobreak >nul

:: Start frontend (in a new window)
echo Starting frontend service...
start cmd /k "title OnFinance Frontend && .venv\Scripts\activate.bat && python app/frontend/server.py"

:: Start data integration (optional, in a new window)
echo Starting data integration service...
start cmd /k "title OnFinance Data Integration && .venv\Scripts\activate.bat && python scripts/data_integration.py"

:: Start monitoring (optional, in a new window)
echo Starting monitoring service...
start cmd /k "title OnFinance Monitoring && .venv\Scripts\activate.bat && python scripts/monitoring.py"

echo All services started! Access the application at http://localhost:8000
