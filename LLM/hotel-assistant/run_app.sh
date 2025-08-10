#!/bin/bash

# Hotel Assistant Application Launcher
# This script checks prerequisites and starts the full application

echo "🏨 Hotel Assistant - Starting Application..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if a port is available
port_available() {
    ! nc -z localhost $1 2>/dev/null
}

# Function to wait for service to be ready
wait_for_service() {
    local url=$1
    local name=$2
    local max_attempts=30
    local attempt=1
    
    echo "⏳ Waiting for $name to be ready..."
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" >/dev/null 2>&1; then
            echo -e "${GREEN}✅ $name is ready!${NC}"
            return 0
        fi
        sleep 2
        ((attempt++))
    done
    echo -e "${RED}❌ $name failed to start within $((max_attempts * 2)) seconds${NC}"
    return 1
}

# Check if we're in the correct directory
if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}❌ Error: Please run this script from the hotel-assistant root directory${NC}"
    exit 1
fi

echo "🔍 Checking prerequisites..."

# Check Python
if ! command_exists python3; then
    echo -e "${RED}❌ Python 3 is required but not installed${NC}"
    exit 1
fi

# Check Node.js
if ! command_exists node; then
    echo -e "${RED}❌ Node.js is required but not installed${NC}"
    exit 1
fi

# Check npm
if ! command_exists npm; then
    echo -e "${RED}❌ npm is required but not installed${NC}"
    exit 1
fi

# Check curl for health checks
if ! command_exists curl; then
    echo -e "${RED}❌ curl is required for health checks but not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ All prerequisites satisfied${NC}"

# Load environment variables
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
    echo "📋 Environment variables loaded from .env"
else
    echo -e "${YELLOW}⚠️ Warning: .env file not found, using defaults${NC}"
    export ES_URL=${ES_URL:-"http://localhost:9200"}
    export ES_INDEX=${ES_INDEX:-"hotels"}
fi

# Check Elasticsearch availability
echo "🔍 Checking Elasticsearch connectivity..."
if curl -s "$ES_URL/_cluster/health" >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Elasticsearch is available at $ES_URL${NC}"
    
    # Check if index exists and has documents
    index_response=$(curl -s "$ES_URL/$ES_INDEX/_stats" 2>/dev/null)
    if echo "$index_response" | grep -q "docs.*count"; then
        doc_count=$(echo "$index_response" | grep -o '"count":[0-9]*' | head -1 | cut -d':' -f2)
        if [ "$doc_count" -gt 0 ] 2>/dev/null; then
            echo -e "${GREEN}✅ Index '$ES_INDEX' contains $doc_count documents${NC}"
        else
            echo -e "${YELLOW}⚠️ Warning: Index '$ES_INDEX' exists but contains no documents${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️ Warning: Index '$ES_INDEX' may not exist or be accessible${NC}"
    fi
else
    echo -e "${RED}❌ Elasticsearch is not available at $ES_URL${NC}"
    echo -e "${YELLOW}Please ensure Elasticsearch is running and accessible${NC}"
    exit 1
fi

# Check if ports are available
echo "🔍 Checking port availability..."
if ! port_available 8000; then
    echo -e "${RED}❌ Port 8000 is already in use${NC}"
    exit 1
fi

if ! port_available 3000; then
    echo -e "${RED}❌ Port 3000 is already in use${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Ports 8000 and 3000 are available${NC}"

# Setup Python environment
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

echo "🔄 Activating Python virtual environment..."
source venv/bin/activate

echo "📦 Installing/updating Python dependencies..."
pip install -r requirements.txt >/dev/null 2>&1

# Setup frontend dependencies
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    cd frontend
    npm install >/dev/null 2>&1
    cd ..
fi

# Function to cleanup processes on exit
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        echo "✅ Backend stopped"
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
        echo "✅ Frontend stopped"
    fi
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup INT TERM

echo "🚀 Starting services..."

# Start FastAPI backend
echo "🔧 Starting FastAPI backend on port 8000..."
echo "🐛 Testing backend startup..."
if ! (cd app && python -c "import main; print('✅ FastAPI app imports successfully')"); then
    echo -e "${RED}❌ Backend import failed. Check dependencies and code.${NC}"
    exit 1
fi
(cd app && python -m uvicorn main:app --reload --port 8000 --log-level error) >/dev/null 2>&1 &
BACKEND_PID=$!

# Wait for backend to be ready
if ! wait_for_service "http://localhost:8000/docs" "FastAPI Backend"; then
    cleanup
    exit 1
fi

# Start NextJS frontend
echo "🎨 Starting NextJS frontend on port 3000..."
(cd frontend && npm run dev) >/dev/null 2>&1 &
FRONTEND_PID=$!

# Wait for frontend to be ready
if ! wait_for_service "http://localhost:3000" "NextJS Frontend"; then
    cleanup
    exit 1
fi

echo ""
echo -e "${GREEN}🎉 Hotel Assistant is now running!${NC}"
echo ""
echo -e "${BLUE}📱 Chat Interface: http://localhost:3000${NC}"
echo -e "${BLUE}🔧 Backend API: http://localhost:8000${NC}"
echo -e "${BLUE}📚 API Documentation: http://localhost:8000/docs${NC}"
echo ""

# Open browser automatically
if command_exists open; then
    echo "🌐 Opening chat interface in browser..."
    sleep 2
    open http://localhost:3000
elif command_exists xdg-open; then
    echo "🌐 Opening chat interface in browser..."
    sleep 2
    xdg-open http://localhost:3000
elif command_exists start; then
    echo "🌐 Opening chat interface in browser..."
    sleep 2
    start http://localhost:3000
else
    echo -e "${YELLOW}💡 Please open http://localhost:3000 in your browser${NC}"
fi

echo "Press Ctrl+C to stop all services"

# Keep script running and wait for processes
wait
