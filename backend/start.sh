#!/bin/bash

# Decode Google credentials if they exist
if [ ! -z "$GOOGLE_CREDENTIALS_BASE64" ]; then
    echo "$GOOGLE_CREDENTIALS_BASE64" | base64 -d > /app/google-credentials.json
fi
# Wait for the database
./wait-for-it.sh ccba8a0vn4fb2p.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432 -t 300 -- echo "Database is up"

# Now we add the google-credentials.json file creation
# Create the google-credentials.json file if it doesn't exist
if [ ! -f "/app/google-credentials.json" ]; then
    echo "Creating google-credentials.json"
    echo "$GOOGLE_CREDENTIALS_BASE64" | base64 -d > /app/google-credentials.json
    chmod 600 /app/google-credentials.json
fi

# Change directory to where alembic.ini is located
cd /app

# Run Alembic migrations
alembic upgrade head

# Start Uvicorn, pointing to api/main.py
exec uvicorn api.main:app --host 0.0.0.0 --port "$PORT"