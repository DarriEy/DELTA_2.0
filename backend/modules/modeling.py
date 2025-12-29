# backend/modules/modeling.py
import os
import sys
import yaml
import tempfile
import shutil
import logging
import traceback
from pathlib import Path
from utils.config import config
from sqlalchemy.orm import Session
from api.models import Job as DBJob

logger = logging.getLogger(__name__)

# Add SYMFLUENCE to path
SYMFLUENCE_CODE_DIR = config.get("SYMFLUENCE_CODE_DIR")
if SYMFLUENCE_CODE_DIR and os.path.exists(SYMFLUENCE_CODE_DIR):
    src_path = str(Path(SYMFLUENCE_CODE_DIR) / "src")
    if src_path not in sys.path:
        sys.path.append(src_path)
        logger.info(f"Added SYMFLUENCE src to sys.path: {src_path}")
    # Also add the root for any other utilities
    if SYMFLUENCE_CODE_DIR not in sys.path:
        sys.path.append(SYMFLUENCE_CODE_DIR)
else:
    logger.warning(f"SYMFLUENCE_CODE_DIR not found: {SYMFLUENCE_CODE_DIR}")

async def execute_modeling_job(job_id: int, db_session_factory):
    """
    Background worker to execute a modeling job using example data.
    """
    db: Session = db_session_factory()
    job = db.query(DBJob).filter(DBJob.id == job_id).first()
    if not job:
        logger.error(f"Job {job_id} not found in database.")
        return

    try:
        job.status = "RUNNING"
        job.logs = "Scientific model execution initialized...\n"
        db.commit()

        from symfluence import SYMFLUENCE

        model_name = job.parameters.get("model", "SUMMA")
        domain = job.parameters.get("watershed", "Bow_at_Banff_lumped")
        
        # Example data path
        base_data_path = Path("/Users/darrieythorsson/compHydro/data/SYMFLUENCE_data")
        domain_data_path = base_data_path / f"domain_{domain}"

        with tempfile.TemporaryDirectory(prefix="delta_model_run_") as tmpdir:
            tmp_path = Path(tmpdir)
            job.logs += f"Workspace created: {tmpdir}\n"
            db.commit()

            # Create domain structure in temp dir
            temp_domain_path = tmp_path / f"domain_{domain}"
            temp_domain_path.mkdir()
            
            # Symlink example data to temp dir to avoid full acquisition
            if domain_data_path.exists():
                job.logs += "Linking example datasets (attributes, forcing, shapefiles)...\n"
                for sub in ['attributes', 'forcing', 'shapefiles']:
                    src = domain_data_path / sub
                    if src.exists():
                        os.symlink(src, temp_domain_path / sub)
                db.commit()
            else:
                job.logs += f"Warning: Example data not found at {domain_data_path}. Initializing empty project.\n"

            # Load template config
            template_path = Path(SYMFLUENCE_CODE_DIR) / "0_config_files" / "config_template.yaml"
            if not template_path.exists():
                template_path = Path(__file__).parent.parent / "examples" / "config_Bow.yaml"

            with open(template_path, 'r') as f:
                model_config = yaml.safe_load(f)

            # Update for temp run
            model_config['DOMAIN_NAME'] = domain
            model_config['EXPERIMENT_ID'] = f"delta_job_{job_id}"
            model_config['HYDROLOGICAL_MODEL'] = model_name
            # SYMFLUENCE usually looks at CONFLUENCE_DATA_DIR or similar
            model_config['CONFLUENCE_DATA_DIR'] = str(tmp_path)
            
            # Save temp config
            temp_config_path = tmp_path / "config.yaml"
            with open(temp_config_path, 'w') as f:
                yaml.dump(model_config, f)

            job.logs += f"SYMFLUENCE initializing with model: {model_name}\n"
            db.commit()

            sf = SYMFLUENCE(str(temp_config_path))
            
            # Setup project structure
            sf.managers['project'].setup_project()
            
            job.logs += "Project structure ready. Ready for mathematical execution.\n"
            # Note: A full run might take too long for a demo, 
            # but we've successfully set up the environment with example data.
            
            job.status = "COMPLETED"
            job.result = {
                "project_dir": str(temp_domain_path),
                "model": model_name,
                "domain": domain,
                "data_linked": domain_data_path.exists(),
                "message": "Modeling workspace successfully established with example scientific data."
            }
            job.logs += "Process complete.\n"
            db.commit()

    except Exception as e:
        error_trace = traceback.format_exc()
        logger.error(f"Modeling job {job_id} failed: {e}")
        job.status = "FAILED"
        job.logs += f"\nERROR: {str(e)}\n{error_trace}"
        db.commit()
    finally:
        db.close()
