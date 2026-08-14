from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN_SCRIPT = ROOT / "servers" / "baseline-fastapi" / "run.sh"


def run_script_text() -> str:
    return RUN_SCRIPT.read_text(encoding="utf-8")


def test_run_script_exists():
    assert RUN_SCRIPT.is_file(), "servers/baseline-fastapi/run.sh must exist"


def test_run_script_sources_baseline_profile():
    assert "profiles/baseline.env" in run_script_text()


def test_run_script_sources_shared_model_config():
    assert "configs/models.env" in run_script_text()


def test_run_script_launches_uvicorn():
    assert "uvicorn" in run_script_text()
    assert "app:app" in run_script_text()
