#!/bin/bash

echo "🚀 Deploying DELTA Backend to Render..."

# Check if we're in the right directory
if [ ! -f "render.yaml" ]; then
    echo "❌ render.yaml not found. Please run from project root."
    exit 1
fi

# Check if backend files exist
if [ ! -f "backend/google-credentials.json" ]; then
    echo "❌ backend/google-credentials.json not found."
    exit 1
fi

echo "✅ Files verified"

# Commit and push changes
echo "📦 Committing changes..."
git add .
git commit -m "Deploy DELTA backend with Google credentials"
git push

echo "🎉 Deployment initiated!"
echo "📍 Your backend will be available at: https://delta-backend-zom0.onrender.com"
echo "⏳ Deployment usually takes 2-3 minutes..."
echo ""
echo "To check deployment status:"
echo "1. Go to https://render.com"
echo "2. Check your delta-backend service"
echo ""
echo "Once deployed, test at: https://darriey.github.io/DELTA_2.0/"
