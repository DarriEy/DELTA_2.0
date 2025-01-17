#!/bin/bash

# Serve the built files from the 'dist' directory using Python's server
python3 -m http.server $PORT --directory dist