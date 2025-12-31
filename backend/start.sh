#!/bin/bash

# Improved credential handling
if [ -n "$GOOGLE_APPLICATION_CREDENTIALS_JSON" ]; then
    echo "Using GOOGLE_APPLICATION_CREDENTIALS_JSON"
    echo $GOOGLE_APPLICATION_CREDENTIALS_JSON > google-credentials.json
    export GOOGLE_APPLICATION_CREDENTIALS=google-credentials.json
elif [ -n "$GOOGLE_APPLICATION_CREDENTIALS_BASE64" ]; then
    echo "Using GOOGLE_APPLICATION_CREDENTIALS_BASE64"
    echo $GOOGLE_APPLICATION_CREDENTIALS_BASE64 | base64 --decode > google-credentials.json
    export GOOGLE_APPLICATION_CREDENTIALS=google-credentials.json
elif [ -n "$GOOGLE_APPLICATION_CREDENTIALS" ] && [[ "$GOOGLE_APPLICATION_CREDENTIALS" == ey* ]]; then
    # If the main variable looks like base64
    echo "Decoding GOOGLE_APPLICATION_CREDENTIALS from base64"
    echo $GOOGLE_APPLICATION_CREDENTIALS | base64 --decode > google-credentials.json
    export GOOGLE_APPLICATION_CREDENTIALS=google-credentials.json
fi

# Apply database migrations
echo "Applying database migrations..."
alembic upgrade head || echo "Migration failed, but continuing..."

# Start the FastAPI application using uvicorn
echo "Starting DELTA Backend on port $PORT..."
uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000}