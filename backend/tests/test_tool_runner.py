import pytest
pytest.importorskip("sqlalchemy")

from unittest.mock import MagicMock
from backend.api.services.tool_runner import run_tools


def test_run_tools_handles_missing_background_tasks():
    db = MagicMock()
    results = run_tools(
        db,
        None,
        [{"name": "run_model", "args": {"model": "SUMMA"}}],
    )

    assert results[0]["name"] == "run_model"
    assert "Background tasks not available" in results[0]["result"]


def test_run_tools_handles_unknown_tool():
    db = MagicMock()
    results = run_tools(db, None, [{"name": "mystery", "args": {}}])

    assert results[0]["name"] == "mystery"
    assert "Unknown tool" in results[0]["result"]
