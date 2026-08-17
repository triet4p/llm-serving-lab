from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNERS = {
    "baseline": ROOT / "servers" / "baseline-fastapi" / "run.sh",
    "vllm": ROOT / "servers" / "vllm" / "run.sh",
    "ollama": ROOT / "servers" / "ollama" / "run.sh",
}


def runner_text(name: str) -> str:
    return RUNNERS[name].read_text(encoding="utf-8")


def test_run_scripts_exist():
    for name, path in RUNNERS.items():
        assert path.is_file(), f"servers/{name}/run.sh must exist"


def test_all_runners_respect_exported_model_name():
    for name in RUNNERS:
        text = runner_text(name)
        assert "PRE_MODEL=\"${MODEL_NAME:-}\"" in text
        assert 'export MODEL_NAME="${PRE_MODEL:-$MODEL_NAME}"' in text


def test_baseline_pre_downloads_model():
    text = runner_text("baseline")
    assert "Pre-downloading model" in text
    assert "uv run python" in text
    assert "snapshot_download('$MODEL_NAME')" in text


def test_vllm_pre_downloads_model():
    text = runner_text("vllm")
    assert "Pre-downloading model" in text
    assert "uv run python" in text
    assert "snapshot_download('$MODEL_NAME')" in text


def test_ollama_pulls_model():
    text = runner_text("ollama")
    assert "Pulling model" in text
    assert "ollama pull" in text
    assert '"$MODEL_NAME"' in text
