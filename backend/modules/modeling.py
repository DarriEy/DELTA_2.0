# backend/modules/modeling.py
import os
import sys
import yaml
import tempfile
import shutil
import logging
import traceback
from pathlib import Path
from utils.config import get_settings
from sqlalchemy.orm import Session
from api.models import Job as DBJob

logger = logging.getLogger(__name__)

def get_symfluence_paths():
    settings = get_settings()
    return (
        settings.symfluence_code_dir,
        settings.symfluence_data_dir,
    )


def add_symfluence_to_path(code_dir: str) -> bool:
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


def resolve_domain_data_path(domain: str, base_data_dir: str) -> Path:
    return Path(base_data_dir) / f"domain_{domain}"

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

        code_dir, data_dir = get_symfluence_paths()
        add_symfluence_to_path(code_dir)

        from symfluence import SYMFLUENCE

        model_name = job.parameters.get("model", "SUMMA")
        domain = job.parameters.get("watershed", "Bow_at_Banff_lumped")
        
        # Example data path
        base_data_path = Path(data_dir) if data_dir else Path.cwd()
        domain_data_path = resolve_domain_data_path(domain, str(base_data_path))

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
            template_path = None
            if code_dir:
                template_path = Path(code_dir) / "0_config_files" / "config_template.yaml"
            if not template_path or not template_path.exists():
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
