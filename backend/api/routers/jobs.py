from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from ..models import get_db, SessionLocal
from ..services import job_service
from ..schemas import Job, JobUpdate
from typing import List

router = APIRouter()

@router.post("/run_modeling")
async def run_modeling(
    input_data: dict, 
    background_tasks: BackgroundTasks, 
    db: Session = Depends(get_db)
):
    try:
        new_job = job_service.create_modeling_job(db, input_data, background_tasks, SessionLocal)
        return {"message": f"{new_job.type} job submitted and running", "job_id": new_job.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/jobs/pending", response_model=List[Job])
async def get_pending_jobs(db: Session = Depends(get_db)):
    return job_service.get_pending_jobs(db)

@router.get("/jobs/{job_id}", response_model=Job)
async def get_job(job_id: int, db: Session = Depends(get_db)):
    job = job_service.get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.patch("/jobs/{job_id}", response_model=Job)
async def update_job(job_id: int, update_data: JobUpdate, db: Session = Depends(get_db)):
    job = job_service.get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if update_data.status:
        job.status = update_data.status
    if update_data.result:
        job.result = update_data.result
    if update_data.logs:
        job.logs = update_data.logs
        
    db.commit()
    db.refresh(job)
    return job
