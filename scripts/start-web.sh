#!/bin/bash
# Start script for Batch2MD web interface
# This script starts both the backend API and frontend dev server

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Batch2MD Web Interface Starter${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if we're in the project root
if [ ! -f "pyproject.toml" ]; then
    echo -e "${RED}Error: Please run this script from the project root directory${NC}"
    exit 1
fi

# Check Python dependencies
echo -e "${GREEN}Checking Python dependencies...${NC}"
if ! command -v uv &> /dev/null; then
    echo -e "${RED}Error: 'uv' not found. Please install uv first.${NC}"
    exit 1
fi

# Install Python web dependencies if needed
echo -e "${GREEN}Installing Python dependencies...${NC}"
uv sync --extra web

# Check Node.js/npm
echo -e "${GREEN}Checking Node.js dependencies...${NC}"
if ! command -v npm &> /dev/null; then
    echo -e "${RED}Error: 'npm' not found. Please install Node.js first.${NC}"
    exit 1
fi

# Install frontend dependencies if needed
if [ ! -d "frontend/node_modules" ]; then
    echo -e "${GREEN}Installing frontend dependencies...${NC}"
    cd frontend
    npm install
    cd ..
fi

# Create log directory
mkdir -p logs

echo ""
echo -e "${GREEN}Starting services...${NC}"
echo -e "${BLUE}Backend API will run on: http://localhost:8000${NC}"
echo -e "${BLUE}Frontend will run on: http://localhost:5173${NC}"
echo ""
echo -e "${GREEN}Press Ctrl+C to stop all services${NC}"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo -e "${BLUE}Shutting down services...${NC}"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup INT TERM

# Start backend in background
echo -e "${GREEN}[1/2] Starting backend API...${NC}"
uv run batch2md-web > logs/backend.log 2>&1 &
BACKEND_PID=$!

# Wait a bit for backend to start
sleep 2

# Check if backend is running
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo -e "${RED}Error: Backend failed to start. Check logs/backend.log${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Backend started (PID: $BACKEND_PID)${NC}"

# Start frontend in background
echo -e "${GREEN}[2/2] Starting frontend dev server...${NC}"
cd frontend
npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

# Wait a bit for frontend to start
sleep 3

# Check if frontend is running
if ! kill -0 $FRONTEND_PID 2>/dev/null; then
    echo -e "${RED}Error: Frontend failed to start. Check logs/frontend.log${NC}"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

echo -e "${GREEN}✓ Frontend started (PID: $FRONTEND_PID)${NC}"
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  All services are running!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "📱 Frontend: ${BLUE}http://localhost:5173${NC}"
echo -e "🔌 Backend API: ${BLUE}http://localhost:8000${NC}"
echo -e "📚 API Docs: ${BLUE}http://localhost:8000/docs${NC}"
echo ""
echo -e "📋 Logs:"
echo -e "  - Backend: logs/backend.log"
echo -e "  - Frontend: logs/frontend.log"
echo ""
echo -e "${GREEN}Press Ctrl+C to stop all services${NC}"
echo ""

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
