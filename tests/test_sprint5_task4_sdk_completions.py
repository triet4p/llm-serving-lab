from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "clients" / "openai-sdk" / "completions.py"


def script_text() -> str:
    return SCRIPT.read_text(encoding="utf-8")


def test_completions_script_exists():
    assert SCRIPT.is_file(), "clients/openai-sdk/completions.py must exist"


def test_completions_uses_openai_sdk():
    assert "from openai import OpenAI" in script_text()


def test_completions_configures_client_from_env():
    text = script_text()
    assert "OPENAI_BASE_URL" in text
    assert "OPENAI_API_KEY" in text
    assert "MODEL_NAME" in text


def test_completions_calls_prompt_completions_endpoint():
    assert "completions.create" in script_text()


def test_completions_has_env_script_metadata():
    assert "uv run --script" in script_text()
    assert '"openai' in script_text()
