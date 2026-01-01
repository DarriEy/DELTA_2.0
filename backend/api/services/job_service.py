from typing import List, Optional, Any, Dict
from sqlalchemy.orm import Session
from ..models import Job as DBJob
from modules.modeling import execute_modeling_job
try:
    from fastapi import BackgroundTasks
except ImportError:
    class BackgroundTasks:
        pass

class JobService:
    def create_modeling_job(
        self, 
        db: Session, 
        input_data: Dict[str, Any], 
        background_tasks: BackgroundTasks, 
        session_factory: Any
    ) -> DBJob:
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

    def get_job(self, db: Session, job_id: int) -> Optional[DBJob]:
        return db.query(DBJob).filter(DBJob.id == job_id).first()

    def get_pending_jobs(self, db: Session) -> List[DBJob]:
        return db.query(DBJob).filter(DBJob.status == "PENDING").all()

    def cancel_job(self, db: Session, job_id: int) -> Optional[DBJob]:
        job = self.get_job(db, job_id)
        if not job:
            return None
        
        if job.status in ["PENDING", "RUNNING"]:
            job.status = "CANCELLED"
            db.commit()
            db.refresh(job)
        return job

    def cleanup_stalled_jobs(self, db: Session) -> int:
        """Marks RUNNING or PENDING jobs as STALLED on startup."""
        stalled_jobs = db.query(DBJob).filter(DBJob.status.in_(["RUNNING", "PENDING"])).all()
        for job in stalled_jobs:
            job.status = "STALLED"
            job.logs = (job.logs or "") + "\nJob marked as STALLED due to server restart.\n"
        
        if stalled_jobs:
            db.commit()
        return len(stalled_jobs)

_SERVICE: Optional[JobService] = None

def get_job_service() -> JobService:
    global _SERVICE
    if _SERVICE is None:
        _SERVICE = JobService()
    return _SERVICE