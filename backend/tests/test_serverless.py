import json
import os
import subprocess
import sys
from pathlib import Path
from tempfile import gettempdir

from app.core.config import ROOT, Settings


def test_vercel_uses_temporary_cache_and_disables_persistence(monkeypatch, tmp_path):
    monkeypatch.setenv("VERCEL", "1")
    monkeypatch.setenv("FINQUANT_DATA_DIR", str(tmp_path / "read-only-project"))
    monkeypatch.setenv("FINQUANT_PERSISTENCE_ENABLED", "true")
    config = Settings(_env_file=None)
    assert config.data_dir == Path(gettempdir()) / "finquant-ai"
    assert config.persistence_enabled is False
    assert not (tmp_path / "read-only-project").exists()


def test_local_storage_configuration_is_preserved(tmp_path):
    config = Settings(vercel=False, FINQUANT_DATA_DIR=tmp_path, FINQUANT_PERSISTENCE_ENABLED=True)
    assert config.data_dir == tmp_path
    assert config.persistence_enabled is True


def test_deployment_entrypoint_imports_without_pythonpath():
    env = {key: value for key, value in os.environ.items() if key != "PYTHONPATH"}
    env["VERCEL"] = "1"
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import json; from app.main import app; "
            "from fastapi.testclient import TestClient; "
            "print(json.dumps(TestClient(app).get('/api/health').json()))",
        ],
        cwd=ROOT / "backend",
        env=env,
        text=True,
        capture_output=True,
        check=True,
        timeout=30,
    )
    assert json.loads(result.stdout)["persistence_enabled"] is False
