from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "clients" / "openai-sdk" / "responses.py"


def script_text() -> str:
    return SCRIPT.read_text(encoding="utf-8")


def test_responses_script_exists():
    assert SCRIPT.is_file(), "clients/openai-sdk/responses.py must exist"


def test_responses_uses_openai_sdk():
    assert "from openai import OpenAI" in script_text()


def test_responses_configures_client_from_env():
    text = script_text()
    assert "OPENAI_BASE_URL" in text
    assert "OPENAI_API_KEY" in text
    assert "MODEL_NAME" in text


def test_responses_calls_responses_endpoint():
    assert "responses.create" in script_text()


def test_responses_notes_per_backend_capability():
    assert "per-backend" in script_text()


def test_responses_has_env_script_metadata():
    assert "uv run --script" in script_text()
    assert '"openai' in script_text()
