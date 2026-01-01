import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from backend.api.services.job_service import get_job_service
from backend.api.models import Job as DBJob

@pytest.fixture
def db():
    return MagicMock(spec=Session)

@pytest.fixture
def job_service():
    return get_job_service()

def test_create_modeling_job(db, job_service):
    input_data = {"model": "VIC", "job_type": "SIMULATION"}
    background_tasks = MagicMock()
    session_factory = MagicMock()

    with patch("backend.api.services.job_service.execute_modeling_job") as mock_execute:
        job = job_service.create_modeling_job(db, input_data, background_tasks, session_factory)

    assert job.type == "SIMULATION"
    assert job.parameters["model"] == "VIC"
    assert job.status == "PENDING"
    db.add.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once()
    background_tasks.add_task.assert_called_once()

def test_get_job(db, job_service):
    mock_job = DBJob(id=1, type="SIMULATION", status="COMPLETED")
    db.query.return_value.filter.return_value.first.return_value = mock_job

    job = job_service.get_job(db, 1)

    assert job.id == 1
    assert job.status == "COMPLETED"

def test_get_pending_jobs(db, job_service):
    mock_jobs = [DBJob(id=1, status="PENDING"), DBJob(id=2, status="PENDING")]
    db.query.return_value.filter.return_value.all.return_value = mock_jobs

    jobs = job_service.get_pending_jobs(db)

    assert len(jobs) == 2
    assert jobs[0].status == "PENDING"

def test_cancel_job(db, job_service):
    mock_job = DBJob(id=1, status="RUNNING")
    db.query.return_value.filter.return_value.first.return_value = mock_job

    job = job_service.cancel_job(db, 1)

    assert job.status == "CANCELLED"
    db.commit.assert_called_once()
