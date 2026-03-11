@echo off
REM LegalFinance RAG — Startup Script
REM Run both backend and frontend in sequence

echo.
echo ======================================
echo LegalFinance RAG — Full Stack Startup
echo ======================================
echo.

REM Check if .venv exists
if not exist ".venv" (
    echo Error: Virtual environment not found. Run: python -m venv .venv
    pause
    exit /b 1
)

REM Activate venv
call .venv\Scripts\activate.bat

REM Start FastAPI backend in new window
echo Starting FastAPI backend on http://127.0.0.1:8000...
start "LegalFinance Backend" cmd /k "uvicorn app.main:app --reload --port 8000"

REM Wait for backend to start
timeout /t 3 /nobreak

REM Start Chainlit frontend in new window
echo Starting Chainlit frontend on http://127.0.0.1:8501...
set API_BASE_URL=http://127.0.0.1:8000
start "LegalFinance Chainlit" cmd /k "python -m chainlit run chainlit_app/app.py --port 8501"

echo.
echo ======================================
echo Both services are starting...
echo Backend:  http://127.0.0.1:8000
echo Frontend: http://127.0.0.1:8501
echo ======================================
echo.
pause
