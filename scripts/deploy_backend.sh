#!/bin/bash

# Deployment script for backend updates
# Run this on your EC2 server after pushing code changes

set -e  # Exit on error

echo "🚀 Deploying Backend Updates"
echo "================================"

# 1. Pull latest changes
echo ""
echo "📥 Step 1: Pulling latest code..."
git pull origin main

# 2. Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "⚠️  No virtual environment found. Creating one..."
    python3 -m venv venv
fi

# 3. Activate virtual environment and install dependencies
echo ""
echo "📦 Step 2: Installing dependencies..."
source venv/bin/activate
pip install -r requirements.txt

# 4. Ask about cleaning state
echo ""
echo "🧹 Step 3: Clean old conversation state?"
echo "This will reset all conversations (recommended after room separation fix)"
read -p "Clean state? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python3 scripts/cleanup_state.py
fi

# 5. Restart the service
echo ""
echo "🔄 Step 4: Restarting backend service..."

# Check if Docker is running
if command -v docker &> /dev/null && docker ps &> /dev/null; then
    echo "Using Docker..."
    docker-compose down
    docker-compose up -d
    echo "✅ Backend restarted with Docker"

# Check if PM2 is running
elif command -v pm2 &> /dev/null; then
    echo "Using PM2..."
    pm2 restart sapiens-backend || pm2 start run.py --name sapiens-backend
    echo "✅ Backend restarted with PM2"

# Fallback to manual restart
else
    echo "Using manual restart..."
    # Kill existing process
    pkill -f "uvicorn" || echo "No existing process found"
    # Start new process in background
    nohup python run.py > logs/backend.log 2>&1 &
    echo "✅ Backend restarted manually"
fi

# 6. Verify the service is running
echo ""
echo "🔍 Step 5: Verifying service..."
sleep 3

# Check if backend responds
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend is running!"
    curl -s http://localhost:8000/health | python3 -m json.tool
else
    echo "❌ Backend health check failed!"
    echo "Check logs for errors:"
    echo "  Docker: docker-compose logs -f"
    echo "  PM2: pm2 logs sapiens-backend"
    echo "  Manual: tail -f logs/backend.log"
    exit 1
fi

echo ""
echo "================================"
echo "✅ Deployment Complete!"
echo ""
echo "Test your changes:"
echo "  1. Create a new room (New Chat)"
echo "  2. Send a message - should be in 'onboarding' phase"
echo "  3. Create another room - should also start in 'onboarding'"
echo ""
