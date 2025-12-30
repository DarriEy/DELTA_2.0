#!/bin/bash
cd backend
source .venv/bin/activate
export PYTHONPATH=$PWD:/Users/darrieythorsson/compHydro/code/SYMFLUENCE/src
uvicorn api.main:app --port 8000 &
BACKEND_PID=$!
sleep 5
python3 test_modeling_trigger.py
kill $BACKEND_PID
