# backend/test_modeling_trigger.py
import requests
import time
import sys

BASE_URL = "http://localhost:8000/api"

def test_run_modeling():
    payload = {
        "model": "SUMMA",
        "job_type": "SIMULATION"
    }
    
    print(f"Triggering modeling job for {payload['model']}...")
    try:
        response = requests.post(f"{BASE_URL}/run_modeling", json=payload)
        response.raise_for_status()
        data = response.json()
        job_id = data.get("job_id")
        print(f"Job submitted successfully. Job ID: {job_id}")
        
        # Poll for status
        for _ in range(10):
            time.sleep(2)
            status_res = requests.get(f"{BASE_URL}/jobs/{job_id}")
            status_data = status_res.json()
            status = status_data.get("status")
            print(f"Job Status: {status}")
            
            if status in ["COMPLETED", "FAILED"]:
                print("Job finished.")
                if status == "COMPLETED":
                    print("Result:", status_data.get("result"))
                else:
                    print("Logs:", status_data.get("logs"))
                break
        else:
            print("Job timed out or still running.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_run_modeling()
