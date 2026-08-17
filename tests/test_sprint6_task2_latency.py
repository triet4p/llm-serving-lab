from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "benchmarks" / "latency.py"


def script_text() -> str:
    return SCRIPT.read_text(encoding="utf-8")


def test_latency_script_exists():
    assert SCRIPT.is_file(), "benchmarks/latency.py must exist"


def test_latency_uses_env_contract():
    text = script_text()
    for var in ("OPENAI_BASE_URL", "OPENAI_API_KEY", "MODEL_NAME"):
        assert var in text, f"benchmark must read env var: {var}"


def test_latency_uses_inline_script_metadata():
    text = script_text()
    assert "uv run --script" in text
    assert '"httpx' in text


def test_latency_runs_repeated_requests():
    text = script_text()
    assert "--iterations" in text
    assert "range(args.iterations)" in text


def test_latency_aggregates_statistics():
    text = script_text()
    for stat in ("min", "max", "mean", "p50", "p90", "p95"):
        assert stat in text, f"aggregation must include: {stat}"
    assert "statistics.fmean" in text


def test_latency_measures_ttft_and_total():
    text = script_text()
    assert "time_to_first_token" in text
    assert "total_time" in text
    assert "time.perf_counter()" in text
