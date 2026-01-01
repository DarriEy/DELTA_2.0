#!/bin/bash
set -e

echo "🚀 DELTA Deployment Script"
echo "=========================="

# Run tests first
echo "📋 Running test suite..."
cd backend
source .venv/bin/activate
python -m pytest tests/ -q
cd ..

# Build containers
echo "🐳 Building Docker containers..."
docker compose build --no-cache

# Test containers can start
echo "🔍 Testing container startup..."
docker compose up -d
sleep 10

# Health check
echo "❤️ Running health check..."
curl -f http://localhost:3000/api/health || {
    echo "❌ Health check failed"
    docker compose logs
    docker compose down
    exit 1
}

echo "✅ All checks passed!"
echo "🎉 Ready for deployment!"

# Cleanup
docker compose down

echo "To deploy:"
echo "  git add ."
echo "  git commit -m 'feat: major refactoring - containerization, API consolidation, monorepo optimization'"
echo "  git push origin main"
