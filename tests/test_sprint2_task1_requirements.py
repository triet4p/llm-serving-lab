from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIREMENTS = ROOT / "servers" / "baseline-fastapi" / "requirements.txt"


def requirements_text() -> str:
    return REQUIREMENTS.read_text(encoding="utf-8")


def test_requirements_file_exists():
    assert REQUIREMENTS.is_file(), "servers/baseline-fastapi/requirements.txt must exist"


def test_requirements_pin_fastapi():
    assert "fastapi==" in requirements_text()


def test_requirements_pin_uvicorn():
    assert "uvicorn==" in requirements_text()


def test_requirements_pin_transformers():
    assert "transformers==" in requirements_text()


def test_requirements_pin_torch():
    assert "torch==" in requirements_text()
