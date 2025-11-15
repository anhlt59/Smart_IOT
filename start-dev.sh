#!/bin/bash

# Script to start both backend and frontend in development mode

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Starting IoT Monitoring Application in Development Mode${NC}"
echo ""

# Start backend (serverless offline) in background
echo -e "${GREEN}Starting backend on http://localhost:3000${NC}"
cd /home/user/Smart_IOT/backend
npm run dev &
BACKEND_PID=$!

# Wait for backend to start
sleep 5

# Start frontend in background
echo -e "${GREEN}Starting frontend on http://localhost:5173${NC}"
cd /home/user/Smart_IOT/frontend
npm run dev &
FRONTEND_PID=$!

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}Backend running at: http://localhost:3000${NC}"
echo -e "${GREEN}Frontend running at: http://localhost:5173${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for user interrupt
trap "echo 'Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
