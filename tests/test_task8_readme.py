import re
from pathlib import Path

README = Path(__file__).resolve().parents[1] / "README.md"


def readme_text() -> str:
    return README.read_text(encoding="utf-8")


def test_no_longer_planning_phase():
    assert "planning phase" not in readme_text().lower()


def test_describes_run_backends():
    text = readme_text()
    for target in ("serve-baseline", "serve-vllm", "serve-ollama"):
        assert target in text, f"README must document `make {target}`"


def test_describes_config_contract():
    text = readme_text()
    for var in ("OPENAI_BASE_URL", "OPENAI_API_KEY", "MODEL_NAME"):
        assert var in text, f"README must document {var}"


def test_describes_prereqs_and_dev():
    text = readme_text()
    assert re.search(r"Prerequisites", text, re.IGNORECASE)
    assert "uv run pytest" in text
