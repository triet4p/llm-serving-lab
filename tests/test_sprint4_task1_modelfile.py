from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODELFILE = ROOT / "servers" / "ollama" / "Modelfile"


def modelfile_text() -> str:
    return MODELFILE.read_text(encoding="utf-8")


def test_modelfile_exists():
    assert MODELFILE.is_file(), "servers/ollama/Modelfile must exist"


def test_modelfile_defines_base_model():
    assert "FROM qwen3:8b" in modelfile_text()


def test_modelfile_defines_serving_parameters():
    text = modelfile_text()
    for param in ("num_ctx", "temperature", "num_predict"):
        assert f"PARAMETER {param}" in text, f"Modelfile must set PARAMETER {param}"
