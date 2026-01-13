#!/bin/bash

# Deployment script for Outdoor Adventure Gear Catalog Search
# This script sets up the environment and starts both backend and frontend services

set -e  # Exit on any error

echo "=== Outdoor Adventure Gear Catalog Search - Deployment ==="
echo ""

# Check prerequisites
echo "Checking prerequisites..."

# Check for uv or Python venv
if command -v uv &> /dev/null; then
    echo "✓ uv found"
    USE_UV=true
elif command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
    if [[ $(echo "$PYTHON_VERSION >= 3.12" | bc -l 2>/dev/null || echo "0") == "1" ]] || [[ "$PYTHON_VERSION" == "3.12"* ]]; then
        echo "✓ Python 3.12+ found"
        USE_UV=false
    else
        echo "✗ Python 3.12+ required. Found: $PYTHON_VERSION"
        exit 1
    fi
else
    echo "✗ Python 3.12+ or uv required"
    exit 1
fi

# Check for Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$NODE_VERSION" -ge 18 ]; then
        echo "✓ Node.js 18+ found: $(node --version)"
    else
        echo "✗ Node.js 18+ required. Found: $(node --version)"
        exit 1
    fi
else
    echo "✗ Node.js 18+ required"
    exit 1
fi

# Check for npm
if command -v npm &> /dev/null; then
    echo "✓ npm found: $(npm --version)"
else
    echo "✗ npm required"
    exit 1
fi

echo ""
echo "Prerequisites check complete!"
echo ""

# Check if ports are in use
echo "Checking port availability..."
if lsof -ti:8000 &> /dev/null; then
    echo "⚠ Port 8000 is in use. Stopping existing process..."
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    sleep 1
fi

if lsof -ti:3000 &> /dev/null; then
    echo "⚠ Port 3000 is in use. Stopping existing process..."
    lsof -ti:3000 | xargs kill -9 2>/dev/null || true
    sleep 1
fi

echo "✓ Ports 8000 and 3000 are available"
echo ""

# Backend setup
echo "=== Backend Setup ==="
cd backend

# Create virtual environment
if [ "$USE_UV" = true ]; then
    echo "Creating virtual environment with uv..."
    uv venv --python python3.12 venv || python3.12 -m venv venv
    source venv/bin/activate
    echo "Installing backend dependencies..."
    uv pip install -r requirements.txt || pip install -r requirements.txt
else
    echo "Creating virtual environment..."
    python3.12 -m venv venv
    source venv/bin/activate
    echo "Installing backend dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
fi

cd ..
echo "✓ Backend dependencies installed"
echo ""

# Frontend setup
echo "=== Frontend Setup ==="
cd frontend

if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
else
    echo "Frontend dependencies already installed"
fi

cd ..
echo "✓ Frontend dependencies installed"
echo ""

# Start backend
echo "=== Starting Backend Server ==="
cd backend
VENV_PYTHON="$(pwd)/venv/bin/python"
cd ..
nohup "$VENV_PYTHON" -m uvicorn backend.api:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > backend.pid
echo "✓ Backend server started (PID: $BACKEND_PID)"
echo "  Logs: backend.log"
echo ""

# Wait a moment for backend to start
sleep 2

# Start frontend
echo "=== Starting Frontend Server ==="
cd frontend
nohup npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > ../frontend.pid
cd ..
echo "✓ Frontend server started (PID: $FRONTEND_PID)"
echo "  Logs: frontend.log"
echo ""

# Wait a moment for frontend to start
sleep 3

# Verify services
echo "=== Verifying Services ==="
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✓ Backend is responding at http://localhost:8000"
else
    echo "⚠ Backend may not be ready yet. Check backend.log for details."
fi

if curl -s http://localhost:3000 > /dev/null; then
    echo "✓ Frontend is responding at http://localhost:3000"
else
    echo "⚠ Frontend may not be ready yet. Check frontend.log for details."
fi

echo ""
echo "=== Deployment Complete ==="
echo ""
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo ""
echo "To stop services, run: ./destroy.sh"
echo ""
