from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "benchmarks" / "single_request.py"


def script_text() -> str:
    return SCRIPT.read_text(encoding="utf-8")


def test_single_request_script_exists():
    assert SCRIPT.is_file(), "benchmarks/single_request.py must exist"


def test_single_request_uses_env_contract():
    text = script_text()
    for var in ("OPENAI_BASE_URL", "OPENAI_API_KEY", "MODEL_NAME"):
        assert var in text, f"benchmark must read env var: {var}"


def test_single_request_hard_fails_on_missing_env():
    assert "Missing required env var" in script_text()


def test_single_request_uses_inline_script_metadata():
    text = script_text()
    assert "uv run --script" in text
    assert '"httpx' in text


def test_single_request_uses_httpx_streaming():
    text = script_text()
    assert "httpx.Client" in text
    assert "client.stream" in text


def test_single_request_measures_monotonic_timings():
    text = script_text()
    assert "time.perf_counter()" in text
    assert "time_to_first_token" in text
    assert "tokens_per_second" in text


def test_single_request_targets_chat_completions():
    assert "/chat/completions" in script_text()
