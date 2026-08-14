from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN_SCRIPT = ROOT / "servers" / "vllm" / "run.sh"


def run_script_text() -> str:
    return RUN_SCRIPT.read_text(encoding="utf-8")


def test_run_script_exists():
    assert RUN_SCRIPT.is_file(), "servers/vllm/run.sh must exist"


def test_run_script_sources_vllm_profile():
    assert "profiles/vllm.env" in run_script_text()


def test_run_script_sources_shared_model_config():
    assert "configs/models.env" in run_script_text()


def test_run_script_sources_per_server_config():
    assert "servers/vllm/config.env" in run_script_text()


def test_run_script_launches_vllm_serve():
    text = run_script_text()
    assert "vllm serve" in text
    assert "$MODEL_NAME" in text
    assert "--host" in text
    assert "--port" in text


def test_run_script_host_and_port_defaults():
    text = run_script_text()
    assert "0.0.0.0" in text
    assert "8000" in text
