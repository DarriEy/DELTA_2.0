import sys
from pathlib import Path
import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
import yaml

pytest.importorskip("sqlalchemy")

from backend.modules.modeling import ModelingModule, WorkspaceManager
from backend.api.models import Job as DBJob


def test_workspace_manager_domain_path(tmp_path):
    domain = "test_domain"
    with WorkspaceManager(domain, 123, str(tmp_path)) as ws:
        assert ws.get_domain_path() == Path(ws.path) / f"domain_{domain}"


def test_modeling_module_symfluence_path_logic(tmp_path):
    original_sys_path = list(sys.path)
    code_dir = tmp_path / "symfluence"
    (code_dir / "src").mkdir(parents=True)

    settings = MagicMock()
    settings.symfluence_code_dir = str(code_dir)
    
    module = ModelingModule(settings)

    try:
        assert module._add_symfluence_to_path() is True
        assert str(code_dir) in sys.path
        assert str(code_dir / "src") in sys.path
    finally:
        sys.path[:] = original_sys_path


@pytest.mark.asyncio
async def test_modeling_module_execute_success():
    # Mock settings
    settings = MagicMock()
    settings.symfluence_code_dir = None # Use fallback templates
    settings.symfluence_data_dir = None

    # Mock DB and Job
    db = MagicMock(spec=Session)
    job = DBJob(
        id=123, 
        parameters={"model": "SUMMA", "watershed": "test_watershed"},
        status="PENDING",
        logs=""
    )
    db.query.return_value.filter.return_value.first.return_value = job

    module = ModelingModule(settings)

    # Mock SYMFLUENCE and other deps
    with patch("backend.modules.modeling.ModelingModule._add_symfluence_to_path"), \
         patch("backend.modules.modeling.yaml.safe_load", return_value={}), \
         patch("backend.modules.modeling.yaml.dump"), \
         patch("builtins.open", MagicMock()), \
         patch("backend.modules.modeling.WorkspaceManager") as mock_ws_manager:
        
        # Setup WorkspaceManager mock
        ws_instance = mock_ws_manager.return_value.__enter__.return_value
        ws_instance.path = Path("/tmp/mock_ws")
        ws_instance.get_domain_path.return_value = Path("/tmp/mock_ws/domain_test")
        
        # Mock the symfluence module entirely
        mock_sf_module = MagicMock()
        mock_sf_class = mock_sf_module.SYMFLUENCE
        with patch.dict("sys.modules", {"symfluence": mock_sf_module}):
            await module.execute(123, db)
            
            assert job.status == "COMPLETED"
            assert "Process complete" in job.logs
            assert job.result["model"] == "SUMMA"
            mock_sf_class.assert_called_once()


@pytest.mark.asyncio
async def test_modeling_module_execute_failure():
    settings = MagicMock()
    db = MagicMock(spec=Session)
    job = DBJob(id=1, parameters={}, logs="")
    db.query.return_value.filter.return_value.first.return_value = job

    module = ModelingModule(settings)

    with patch("backend.modules.modeling.ModelingModule._add_symfluence_to_path", side_effect=RuntimeError("Path error")):
        await module.execute(1, db)
        
        assert job.status == "FAILED"
        assert "ERROR: Path error" in job.logs


@pytest.mark.asyncio
async def test_modeling_module_execute_already_cancelled():
    settings = MagicMock()
    db = MagicMock(spec=Session)
    job = DBJob(id=1, status="CANCELLED", parameters={}, logs="")
    db.query.return_value.filter.return_value.first.return_value = job

    module = ModelingModule(settings)
    
    # It should return early without doing anything
    await module.execute(1, db)
    assert job.status == "CANCELLED"
    assert job.logs == ""