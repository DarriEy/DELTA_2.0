from sqlalchemy.orm import Session
from ..models import Job as DBJob
from modules.modeling import execute_modeling_job
from fastapi import BackgroundTasks

def create_modeling_job(db: Session, input_data: dict, background_tasks: BackgroundTasks, session_factory):
    model = input_data.get("model", "SUMMA")
    job_type = input_data.get("job_type", "SIMULATION")
    
    new_job = DBJob(
        type=job_type,
        parameters={
            "model": model,
            "watershed": "Bow_at_Banff_lumped",
        },
        status="PENDING"
    )
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    
    background_tasks.add_task(execute_modeling_job, new_job.id, session_factory)
    return new_job

def get_job(db: Session, job_id: int):
    return db.query(DBJob).filter(DBJob.id == job_id).first()

def get_pending_jobs(db: Session):
    return db.query(DBJob).filter(DBJob.status == "PENDING").all()
