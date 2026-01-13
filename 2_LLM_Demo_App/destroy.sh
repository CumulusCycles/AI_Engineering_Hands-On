#!/bin/bash

# Teardown script for Outdoor Adventure Gear Catalog Search
# This script stops all services and cleans up generated files

set -e  # Exit on any error

echo "=== Outdoor Adventure Gear Catalog Search - Teardown ==="
echo ""

# Stop backend server
echo "Stopping backend server..."
if [ -f "backend.pid" ]; then
    BACKEND_PID=$(cat backend.pid)
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        kill $BACKEND_PID 2>/dev/null || true
        echo "✓ Stopped backend server (PID: $BACKEND_PID)"
    fi
    rm -f backend.pid
fi

# Always try to stop by port as fallback
if lsof -ti:8000 &> /dev/null; then
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    echo "✓ Stopped process on port 8000"
else
    echo "  No process found on port 8000"
fi

# Stop frontend server
echo "Stopping frontend server..."
if [ -f "frontend.pid" ]; then
    FRONTEND_PID=$(cat frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        kill $FRONTEND_PID 2>/dev/null || true
        echo "✓ Stopped frontend server (PID: $FRONTEND_PID)"
    fi
    rm -f frontend.pid
fi

# Always try to stop by port as fallback
if lsof -ti:3000 &> /dev/null; then
    lsof -ti:3000 | xargs kill -9 2>/dev/null || true
    echo "✓ Stopped process on port 3000"
else
    echo "  No process found on port 3000"
fi

echo ""

# Remove PID files
echo "Cleaning up PID files..."
rm -f backend.pid frontend.pid
echo "✓ PID files removed"

# Remove log files
echo "Cleaning up log files..."
rm -f backend.log frontend.log
echo "✓ Log files removed"

# Remove Python cache
echo "Cleaning up Python cache..."
find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
echo "✓ Python cache removed"

# Remove virtual environment
echo "Cleaning up virtual environment..."
if [ -d "backend/venv" ]; then
    rm -rf backend/venv
    echo "✓ Virtual environment removed"
else
    echo "  Virtual environment not found"
fi

if [ -d "backend/.venv" ]; then
    rm -rf backend/.venv
    echo "✓ Virtual environment (.venv) removed"
fi

# Remove Chroma database
echo "Cleaning up Chroma database..."
if [ -d "backend/.chroma" ]; then
    rm -rf backend/.chroma
    echo "✓ Chroma database removed"
else
    echo "  Chroma database not found"
fi

# Remove product images
echo "Cleaning up product images..."
if [ -d "backend/static/products" ]; then
    rm -rf backend/static/products/*
    echo "✓ Product images removed"
else
    echo "  Product images directory not found"
fi

# Remove node_modules
echo "Cleaning up node_modules..."
if [ -d "frontend/node_modules" ]; then
    rm -rf frontend/node_modules
    echo "✓ node_modules removed"
else
    echo "  node_modules not found"
fi

# Remove build artifacts
echo "Cleaning up build artifacts..."
if [ -d "frontend/dist" ]; then
    rm -rf frontend/dist
    echo "✓ Build artifacts removed"
else
    echo "  Build artifacts not found"
fi

echo ""
echo "=== Teardown Complete ==="
echo ""
echo "All services stopped and files cleaned up."
echo ""
