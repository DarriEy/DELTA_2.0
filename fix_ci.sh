#!/bin/bash
git add backend/api/models.py
git commit -m "Handle missing DATABASE_URL in models.py for CI stability"
git push origin main
