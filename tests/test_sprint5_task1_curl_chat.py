from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CURL_CHAT = ROOT / "clients" / "raw-http" / "curl-chat.sh"


def script_text() -> str:
    return CURL_CHAT.read_text(encoding="utf-8")


def test_curl_chat_script_exists():
    assert CURL_CHAT.is_file(), "clients/raw-http/curl-chat.sh must exist"


def test_curl_chat_targets_chat_completions_endpoint():
    text = script_text()
    assert "curl" in text
    assert "chat/completions" in text


def test_curl_chat_uses_backend_neutral_env_vars():
    text = script_text()
    for var in ("OPENAI_BASE_URL", "OPENAI_API_KEY", "MODEL_NAME"):
        assert var in text, f"curl script must use env var: {var}"


def test_curl_chat_sends_bearer_auth():
    text = script_text()
    assert "Authorization: Bearer" in text
