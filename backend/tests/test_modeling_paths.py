import sys
from pathlib import Path
import pytest

pytest.importorskip("sqlalchemy")

from backend.modules.modeling import add_symfluence_to_path, resolve_domain_data_path


def test_resolve_domain_data_path():
    base = "/data/root"
    path = resolve_domain_data_path("Bow_at_Banff_lumped", base)
    assert path == Path("/data/root/domain_Bow_at_Banff_lumped")


def test_add_symfluence_to_path(tmp_path):
    original_sys_path = list(sys.path)
    code_dir = tmp_path / "symfluence"
    (code_dir / "src").mkdir(parents=True)

    try:
        assert add_symfluence_to_path(str(code_dir)) is True
        assert str(code_dir) in sys.path
        assert str(code_dir / "src") in sys.path
    finally:
        sys.path[:] = original_sys_path
