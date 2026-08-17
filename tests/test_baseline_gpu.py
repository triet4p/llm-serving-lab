from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "servers" / "baseline-fastapi" / "app.py"


def app_text() -> str:
    return APP.read_text(encoding="utf-8")


def test_baseline_uses_gpu_when_available():
    text = app_text()
    assert "import torch" in text
    assert 'torch.device("cuda" if torch.cuda.is_available() else "cpu")' in text


def test_baseline_moves_model_to_device():
    assert ".to(DEVICE)" in app_text()


def test_baseline_moves_inputs_to_device():
    assert "value.to(DEVICE)" in app_text()


def test_baseline_decodes_on_cpu():
    assert "generated.cpu()" in app_text()
