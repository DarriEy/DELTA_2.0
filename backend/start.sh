#!/bin/bash

# Start the FastAPI application using uvicorn
uvicorn api.main:app --host 0.0.0.0 --port $PORT