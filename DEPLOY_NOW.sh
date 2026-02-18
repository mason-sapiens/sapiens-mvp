#!/bin/bash
# Complete deployment script for AWS EC2 backend
# Run this anytime you push backend changes

set -e

echo "🚀 DEPLOYING BACKEND TO AWS EC2"
echo "================================"

# Configuration
EC2_HOST="3.101.121.64"
EC2_USER="ubuntu"
SSH_KEY="$HOME/.ssh/sapiens-mvp-key.pem"
REMOTE_DIR="~/MVP"

echo ""
echo "📋 Step 1: Checking local changes..."
if [[ -n $(git status -s) ]]; then
    echo "⚠️  Warning: You have uncommitted changes!"
    git status -s
    read -p "Continue anyway? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo "📤 Step 2: Copying updated files to server..."

# Copy all backend files
scp -i "$SSH_KEY" -r backend/ "${EC2_USER}@${EC2_HOST}:${REMOTE_DIR}/"
scp -i "$SSH_KEY" -r scripts/ "${EC2_USER}@${EC2_HOST}:${REMOTE_DIR}/"

echo "✅ Files copied"

echo ""
echo "🧹 Step 3: Cleaning old state on server..."
ssh -i "$SSH_KEY" "${EC2_USER}@${EC2_HOST}" "cd ${REMOTE_DIR} && sudo rm -rf data/logs/*"
echo "✅ State cleaned"

echo ""
echo "🔄 Step 4: Restarting backend container..."
ssh -i "$SSH_KEY" "${EC2_USER}@${EC2_HOST}" "cd ${REMOTE_DIR} && docker restart sapiens_app"

echo ""
echo "⏳ Waiting for container to start..."
sleep 10

echo ""
echo "🔍 Step 5: Verifying deployment..."
ssh -i "$SSH_KEY" "${EC2_USER}@${EC2_HOST}" "curl -s http://localhost:8000/health" || {
    echo "❌ Health check failed!"
    echo "Check logs with:"
    echo "  ssh -i $SSH_KEY ${EC2_USER}@${EC2_HOST} 'docker logs --tail 50 sapiens_app'"
    exit 1
}

echo ""
echo "================================"
echo "✅ DEPLOYMENT COMPLETE!"
echo ""
echo "Backend is running at: http://${EC2_HOST}:8000"
echo ""
echo "Test it:"
echo "  curl http://${EC2_HOST}:8000/health"
echo ""
echo "View logs:"
echo "  ssh -i $SSH_KEY ${EC2_USER}@${EC2_HOST} 'docker logs -f sapiens_app'"
echo ""
