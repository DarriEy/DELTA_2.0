#!/bin/bash

npm install
npm run build
python3 -m http.server $PORT --directory dist