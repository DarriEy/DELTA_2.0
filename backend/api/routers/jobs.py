from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from utils.db import get_db, get_session_local
from ..services.job_service import JobService, get_job_service
from ..schemas import Job, JobCreate, JobUpdate, APIResponse
from typing import List, Dict, Any, Optional

router = APIRouter()

@router.post("/run_modeling", response_model=APIResponse[Dict[str, Any]])
async def run_modeling(
    input_data: JobCreate, 
    background_tasks: BackgroundTasks, 
    db: Optional[Session] = Depends(get_db),
    job_service: JobService = Depends(get_job_service)
):
    if not db:
        raise HTTPException(status_code=503, detail="Database required for modeling jobs")
    try:
        session_factory = get_session_local()
        new_job = job_service.create_modeling_job(
            db, input_data.dict(), background_tasks, session_factory
        )
        return APIResponse(data={"message": f"{new_job.type} job submitted and running", "job_id": new_job.id})
    except Exception as e:
        if db:
            db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/jobs/pending", response_model=APIResponse[List[Job]])
async def get_pending_jobs(
    db: Optional[Session] = Depends(get_db),
    job_service: JobService = Depends(get_job_service)
):
    if not db:
        return APIResponse(data=[])
    jobs = job_service.get_pending_jobs(db)
    return APIResponse(data=jobs)

@router.get("/jobs/{job_id}", response_model=APIResponse[Job])
async def get_job(
    job_id: int, 
    db: Optional[Session] = Depends(get_db),
    job_service: JobService = Depends(get_job_service)
):
    if not db:
        raise HTTPException(status_code=404, detail="Job not found (stateless mode)")
    job = job_service.get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return APIResponse(data=job)

@router.post("/jobs/{job_id}/cancel", response_model=APIResponse[Job])
async def cancel_job(
    job_id: int, 
    db: Optional[Session] = Depends(get_db),
    job_service: JobService = Depends(get_job_service)
):
    if not db:
        raise HTTPException(status_code=503, detail="Database required")
    job = job_service.cancel_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return APIResponse(data=job)

@router.patch("/jobs/{job_id}", response_model=APIResponse[Job])
async def update_job(
    job_id: int, 
    update_data: JobUpdate, 
    db: Optional[Session] = Depends(get_db),
    job_service: JobService = Depends(get_job_service)
):
    if not db:
        raise HTTPException(status_code=503, detail="Database required")
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
    return APIResponse(data=job)
