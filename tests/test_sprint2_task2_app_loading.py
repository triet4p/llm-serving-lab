from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "servers" / "baseline-fastapi" / "app.py"


def app_text() -> str:
    return APP.read_text(encoding="utf-8")


def test_app_file_exists():
    assert APP.is_file(), "servers/baseline-fastapi/app.py must exist"


def test_app_creates_fastapi_instance():
    assert "FastAPI(" in app_text()


def test_app_loads_model_name_from_env():
    assert "os.environ.get" in app_text()
    assert "MODEL_NAME" in app_text()


def test_app_uses_auto_tokenizer():
    assert "AutoTokenizer" in app_text()


def test_app_uses_auto_model_for_causal_lm():
    assert "AutoModelForCausalLM" in app_text()


def test_app_defines_load_function():
    assert "def load_model" in app_text()
