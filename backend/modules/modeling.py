# backend/modules/modeling.py
import os
import sys
import yaml
import tempfile
import shutil
import logging
import traceback
from pathlib import Path
from typing import Tuple, Optional, Any, Dict
from utils.config import get_settings, Settings
from sqlalchemy.orm import Session
from api.models import Job as DBJob

logger = logging.getLogger(__name__)

class WorkspaceManager:
    """Handles temporary workspace creation and data linking."""
    def __init__(self, domain: str, job_id: int, data_dir: Optional[str]):
        self.domain = domain
        self.job_id = job_id
        self.data_dir = data_dir
        self.tmp_dir: Optional[tempfile.TemporaryDirectory] = None
        self.path: Optional[Path] = None

    def __enter__(self):
        self.tmp_dir = tempfile.TemporaryDirectory(prefix="delta_model_run_")
        self.path = Path(self.tmp_dir.name)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.tmp_dir:
            self.tmp_dir.cleanup()

    def get_domain_path(self) -> Path:
        return self.path / f"domain_{self.domain}"

    def setup_domain(self, job_logger: Any):
        domain_path = self.get_domain_path()
        domain_path.mkdir()
        
        if not self.data_dir:
            job_logger.append("Warning: Data directory not configured. Initializing empty project.")
            return

        domain_data_path = Path(self.data_dir) / f"domain_{self.domain}"
        if domain_data_path.exists():
            job_logger.append("Linking example datasets (attributes, forcing, shapefiles)...")
            for sub in ['attributes', 'forcing', 'shapefiles']:
                src = domain_data_path / sub
                if src.exists():
                    os.symlink(src, domain_path / sub)
        else:
            job_logger.append(f"Warning: Example data not found at {domain_data_path}.")

class JobLogger:
    def __init__(self, db: Session, job: DBJob):
        self.db = db
        self.job = job

    def append(self, message: str):
        # Refresh from DB to check for cancellation
        self.db.refresh(self.job)
        if self.job.status == "CANCELLED":
            return
        self.job.logs += f"{message}\n"
        self.db.commit()

class ModelingModule:
    def __init__(self, settings: Settings):
        self.settings = settings

    def _add_symfluence_to_path(self) -> bool:
        code_dir = self.settings.symfluence_code_dir
        if not code_dir or not os.path.exists(code_dir):
            logger.warning("SYMFLUENCE_CODE_DIR not found: %s", code_dir)
            return False

        src_path = str(Path(code_dir) / "src")
        if src_path not in sys.path:
            sys.path.append(src_path)
            logger.info("Added SYMFLUENCE src to sys.path: %s", src_path)
        if code_dir not in sys.path:
            sys.path.append(code_dir)
        return True

    def _get_template_path(self) -> Path:
        code_dir = self.settings.symfluence_code_dir
        template_path = None
        if code_dir:
            template_path = Path(code_dir) / "0_config_files" / "config_template.yaml"
        
        if not template_path or not template_path.exists():
            template_path = Path(__file__).parent.parent / "examples" / "config_Bow.yaml"
        
        return template_path

    async def execute(self, job_id: int, db: Session):
        job = db.query(DBJob).filter(DBJob.id == job_id).first()
        if not job:
            logger.error(f"Job {job_id} not found in database.")
            return

        # Check if already cancelled before starting
        if job.status == "CANCELLED":
            logger.info(f"Job {job_id} was cancelled before execution.")
            return

        job_log = JobLogger(db, job)
        
        try:
            job.status = "RUNNING"
            job_log.append("Scientific model execution initialized...")

            self._add_symfluence_to_path()
            from symfluence import SYMFLUENCE

            model_name = job.parameters.get("model", "SUMMA")
            domain = job.parameters.get("watershed", "Bow_at_Banff_lumped")
            
            with WorkspaceManager(domain, job_id, self.settings.symfluence_data_dir) as ws:
                job_log.append(f"Workspace created: {ws.path}")
                ws.setup_domain(job_log)

                template_path = self._get_template_path()
                with open(template_path, 'r') as f:
                    model_config = yaml.safe_load(f)

                model_config.update({
                    'DOMAIN_NAME': domain,
                    'EXPERIMENT_ID': f"delta_job_{job_id}",
                    'HYDROLOGICAL_MODEL': model_name,
                    'CONFLUENCE_DATA_DIR': str(ws.path)
                })
                
                temp_config_path = ws.path / "config.yaml"
                with open(temp_config_path, 'w') as f:
                    yaml.dump(model_config, f)

                job_log.append(f"SYMFLUENCE initializing with model: {model_name}")
                
                sf = SYMFLUENCE(str(temp_config_path))
                sf.managers['project'].setup_project()
                
                job_log.append("Project structure ready. Ready for mathematical execution.")
                
                job.status = "COMPLETED"
                job.result = {
                    "project_dir": str(ws.get_domain_path()),
                    "model": model_name,
                    "domain": domain,
                    "message": "Modeling workspace successfully established."
                }
                job_log.append("Process complete.")

        except Exception as e:
            error_trace = traceback.format_exc()
            logger.error(f"Modeling job {job_id} failed: {e}")
            job.status = "FAILED"
            job.logs += f"\nERROR: {str(e)}\n{error_trace}"
            db.commit()

async def execute_modeling_job(job_id: int, db_session_factory):
    db: Session = db_session_factory()
    try:
        module = ModelingModule(get_settings())
        await module.execute(job_id, db)
    finally:
        db.close()