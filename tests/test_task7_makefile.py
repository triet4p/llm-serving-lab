import re
from pathlib import Path

MAKEFILE = Path(__file__).resolve().parents[1] / "Makefile"
TARGETS = ["serve-baseline", "serve-vllm", "serve-ollama", "smoke", "benchmark", "health"]


def makefile_text() -> str:
    return MAKEFILE.read_text(encoding="utf-8")


def test_required_targets_defined():
    text = makefile_text()
    defined = set(re.findall(r"^([A-Za-z0-9_.-]+):", text, flags=re.MULTILINE))
    for target in TARGETS:
        assert target in defined, f"missing target: {target}"


def test_serve_targets_source_their_profile():
    text = makefile_text()
    for backend in ("baseline", "vllm", "ollama"):
        assert f"$(call load_profile,{backend})" in text, f"serve-{backend} must load profiles/{backend}.env"


def test_profiles_source_shared_model_config():
    assert "configs/models.env" in makefile_text()
