@echo off
REM Quick Start Script for LegalFinance AI Frontend (Windows)
REM This script sets up and runs the frontend in development mode

setlocal enabledelayedexpansion

echo ======================================
echo LegalFinance AI Frontend - Quick Start
echo ======================================
echo.

REM Check if Node.js is installed
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Node.js is not installed. Please install Node.js 18+ from https://nodejs.org/
    exit /b 1
)

for /f "tokens=*" %%i in ('node --version') do set NODE_VERSION=%%i
for /f "tokens=*" %%i in ('npm --version') do set NPM_VERSION=%%i

echo ✅ Node.js version: %NODE_VERSION%
echo ✅ NPM version: %NPM_VERSION%
echo.

REM Check if we're in the right directory
if not exist "package.json" (
    echo ❌ package.json not found. Please run this script from frontend-nextjs directory:
    echo    cd frontend-nextjs
    echo    quickstart.bat
    exit /b 1
)

REM Install dependencies if node_modules doesn't exist
if not exist "node_modules" (
    echo 📦 Installing dependencies...
    call npm install
    if %ERRORLEVEL% NEQ 0 (
        echo ❌ Failed to install dependencies
        exit /b 1
    )
    echo ✅ Dependencies installed
    echo.
)

REM Create .env.local if it doesn't exist
if not exist ".env.local" (
    echo 🔧 Creating .env.local...
    copy .env.example .env.local >nul
    if %ERRORLEVEL% NEQ 0 (
        echo ❌ Failed to create .env.local
        exit /b 1
    )
    echo ✅ Created .env.local
    echo.
    echo    Update .env.local if your backend is not on http://localhost:8000
)

REM Check if backend is running
echo 🔍 Checking backend health...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8000/health' -UseBasicParsing -ErrorAction Stop; Write-Host '✅ Backend is running at http://localhost:8000' } catch { Write-Host '⚠️  Backend doesn''t seem to be running at http://localhost:8000'; Write-Host '   Start it with: python -m uvicorn app.main:app --reload --port 8000' }"

echo.
echo 🚀 Starting frontend on http://localhost:3000...
echo.
echo Press Ctrl+C to stop the server
echo.

call npm run dev
