#!/bin/bash
# 1. Commit Backend Fixes
git add backend/api/main.py backend/utils/google_utils.py
git commit -m "Fix database connection timeout and improve Google credential path discovery"
git push origin main

# 2. Build and Deploy Frontend
cd frontend
npm run build
npm run deploy
