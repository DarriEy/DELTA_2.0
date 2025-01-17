#!/bin/bash

# Decode the base64 encoded credentials
echo $GOOGLE_APPLICATION_CREDENTIALS | base64 --decode > google-credentials.json

# Start the FastAPI application using uvicorn
uvicorn api.main:app --host 0.0.0.0 --port $PORT