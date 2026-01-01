# backend/test_modeling_internal.py
import os
import sys
from fastapi.testclient import TestClient
from pathlib import Path

# Setup paths
PROJECT_ROOT = Path(__file__).parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
SYMFLUENCE_SRC = Path("/Users/darrieythorsson/compHydro/code/SYMFLUENCE/src")

sys.path.append(str(BACKEND_DIR))
sys.path.append(str(SYMFLUENCE_SRC))

from api.main import app
from api.models import Job as DBJob
from utils.db import get_session_local

client = TestClient(app)

def test_modeling_workflow():
    print("--- Starting Internal Modeling Workflow Test ---")
    
    payload = {
        "model": "SUMMA",
        "job_type": "SIMULATION"
    }
    
    print(f"Sending request to /api/run_modeling with {payload}")
    response = client.post("/api/run_modeling", json=payload)
    
    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return

    data = response.json()
    job_id = data.get("job_id")
    print(f"Job created successfully. Job ID: {job_id}")

    # The background task is triggered by FastAPI. 
    # In TestClient, background tasks are usually executed synchronously or need to be handled.
    
    # Let's poll the DB directly
    session_factory = get_session_local()
    if not session_factory:
        print("Skipping DB polling: SessionLocal not initialized.")
        return
    db = session_factory()
    import time
    
    print("Polling database for job status...")
    for i in range(15):
        db.expire_all()
        job = db.query(DBJob).filter(DBJob.id == job_id).first()
        print(f"Attempt {i+1}: Status = {job.status}")
        
        if job.status in ["COMPLETED", "FAILED"]:
            print(f"Job finished with status: {job.status}")
            if job.status == "COMPLETED":
                print("Result:", job.result)
            else:
                print("Logs:", job.logs)
            break
        time.sleep(2)
    else:
        print("Job timed out.")
    
    db.close()

if __name__ == "__main__":
    test_modeling_workflow()
