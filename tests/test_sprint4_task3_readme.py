from pathlib import Path

import re

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "servers" / "ollama" / "README.md"


def readme_text() -> str:
    return README.read_text(encoding="utf-8")


def test_readme_exists():
    assert README.is_file(), "servers/ollama/README.md must exist"


def test_readme_documents_prerequisites():
    text = readme_text()
    for term in ("Ollama installed", "no GPU is required", "curl"):
        assert term in text, f"README must document prerequisite: {term}"


def test_readme_documents_starting_the_server():
    text = readme_text()
    assert "run.sh" in text
    assert "ollama serve" in text
    assert "ollama create" in text
    assert "Modelfile" in text


def test_readme_documents_configuration():
    text = readme_text()
    for var in ("MODEL_NAME", "OLLAMA_HOST", "OPENAI_BASE_URL"):
        assert var in text, f"README must document config var: {var}"


def test_readme_explains_backend_interchangeability():
    text = re.sub(r"\s+", " ", readme_text()).lower()
    assert "backend interchangeability" in text
    assert "client layer stays unchanged" in text
