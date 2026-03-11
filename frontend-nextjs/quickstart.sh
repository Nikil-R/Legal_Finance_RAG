#!/bin/bash
# Quick Start Script for LegalFinance AI Frontend
# This script sets up and runs the frontend in development mode

set -e

echo "======================================"
echo "LegalFinance AI Frontend - Quick Start"
echo "======================================"
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ from https://nodejs.org/"
    exit 1
fi

echo "✅ Node.js version: $(node --version)"
echo "✅ NPM version: $(npm --version)"
echo ""

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ package.json not found. Please run this script from frontend-nextjs directory:"
    echo "   cd frontend-nextjs && bash quickstart.sh"
    exit 1
fi

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
    echo "✅ Dependencies installed"
    echo ""
fi

# Create .env.local if it doesn't exist
if [ ! -f ".env.local" ]; then
    echo "🔧 Creating .env.local..."
    cp .env.example .env.local
    echo "✅ Created .env.local"
    echo ""
    echo "   Update .env.local if your backend is not on http://localhost:8000"
fi

# Check if backend is running
echo "🔍 Checking backend health..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend is running at http://localhost:8000"
else
    echo "⚠️  Backend doesn't seem to be running at http://localhost:8000"
    echo "   Start it with: python -m uvicorn app.main:app --reload --port 8000"
fi

echo ""
echo "🚀 Starting frontend on http://localhost:3000..."
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

npm run dev
