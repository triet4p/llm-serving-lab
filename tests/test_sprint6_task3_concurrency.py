from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "benchmarks" / "concurrency.py"


def script_text() -> str:
    return SCRIPT.read_text(encoding="utf-8")


def test_concurrency_script_exists():
    assert SCRIPT.is_file(), "benchmarks/concurrency.py must exist"


def test_concurrency_uses_env_contract():
    text = script_text()
    for var in ("OPENAI_BASE_URL", "OPENAI_API_KEY", "MODEL_NAME"):
        assert var in text, f"benchmark must read env var: {var}"


def test_concurrency_uses_inline_script_metadata():
    text = script_text()
    assert "uv run --script" in text
    assert '"httpx' in text


def test_concurrency_uses_asyncio_and_httpx():
    text = script_text()
    assert "asyncio" in text
    assert "httpx.AsyncClient" in text
    assert "asyncio.gather" in text


def test_concurrency_uses_semaphore_bounded_parallelism():
    text = script_text()
    assert "asyncio.Semaphore" in text
    assert "--concurrency" in text


def test_concurrency_reports_throughput():
    text = script_text()
    assert "requests/sec" in text
    assert "tokens/sec" in text
