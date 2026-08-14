from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CURL_RESPONSES = ROOT / "clients" / "raw-http" / "curl-responses.sh"


def script_text() -> str:
    return CURL_RESPONSES.read_text(encoding="utf-8")


def test_curl_responses_script_exists():
    assert CURL_RESPONSES.is_file(), "clients/raw-http/curl-responses.sh must exist"


def test_curl_responses_targets_responses_endpoint():
    text = script_text()
    assert "curl" in text
    assert "/responses" in text


def test_curl_responses_uses_backend_neutral_env_vars():
    text = script_text()
    for var in ("OPENAI_BASE_URL", "OPENAI_API_KEY", "MODEL_NAME"):
        assert var in text, f"curl script must use env var: {var}"


def test_curl_responses_sends_bearer_auth():
    text = script_text()
    assert "Authorization: Bearer" in text


def test_curl_responses_notes_per_backend_capability():
    text = script_text()
    assert "per-backend" in text
