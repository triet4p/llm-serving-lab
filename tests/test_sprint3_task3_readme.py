from pathlib import Path

import re

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "servers" / "vllm" / "README.md"


def readme_text() -> str:
    return README.read_text(encoding="utf-8")


def test_readme_exists():
    assert README.is_file(), "servers/vllm/README.md must exist"


def test_readme_documents_gpu_prerequisites():
    text = readme_text()
    for term in ("Linux", "NVIDIA", "driver", "CUDA"):
        assert term in text, f"README must document prerequisite: {term}"


def test_readme_documents_starting_the_server():
    text = readme_text()
    assert "run.sh" in text
    assert "vllm serve" in text
    assert "--host 0.0.0.0" in text
    assert "--port 8000" in text


def test_readme_documents_configuration():
    text = readme_text()
    for var in ("MODEL_NAME", "HOST", "PORT", "TENSOR_PARALLEL_SIZE"):
        assert var in text, f"README must document config var: {var}"


def test_readme_mentions_dev_machine_has_no_gpu():
    text = re.sub(r"\s+", " ", readme_text()).lower()
    assert "does not need a gpu" in text
