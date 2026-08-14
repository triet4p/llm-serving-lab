from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "servers" / "baseline-fastapi" / "app.py"


def app_text() -> str:
    return APP.read_text(encoding="utf-8")


def test_max_tokens_read_from_request_body():
    assert "max_tokens" in app_text()


def test_temperature_read_from_request_body():
    assert "temperature" in app_text()


def test_generate_uses_max_tokens():
    assert "max_new_tokens=request.max_tokens" in app_text()


def test_generate_uses_temperature():
    assert "temperature=request.temperature" in app_text()
