from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN_SCRIPT = ROOT / "servers" / "ollama" / "run.sh"


def run_script_text() -> str:
    return RUN_SCRIPT.read_text(encoding="utf-8")


def test_run_script_exists():
    assert RUN_SCRIPT.is_file(), "servers/ollama/run.sh must exist"


def test_run_script_sources_ollama_profile():
    assert "profiles/ollama.env" in run_script_text()


def test_run_script_sources_shared_model_config():
    assert "configs/models.env" in run_script_text()


def test_run_script_creates_model_from_modelfile():
    text = run_script_text()
    assert "ollama create" in text
    assert "Modelfile" in text
    assert "$MODEL_NAME" in text


def test_run_script_starts_ollama_serve():
    assert "ollama serve" in run_script_text()


def test_run_script_sets_default_ollama_host():
    assert "0.0.0.0:11434" in run_script_text()
