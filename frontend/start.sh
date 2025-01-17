#!/bin/bash

# Install dependencies
npm install

# Build the static production bundle
npm run build

# Serve the built files from the 'dist' directory
# Using Python's simple HTTP server as an example
python3 -m http.server $PORT --directory dist