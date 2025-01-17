#!/bin/bash

# Install dependencies
npm install

# Build the static production bundle
npm run build

# Serve the built files from the 'dist' directory (Vite's default output)
# Using Python's simple HTTP server as an example (you can use others)
python3 -m http.server $PORT --directory frontend/dist