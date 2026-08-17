from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = [
    ROOT / "benchmarks" / "single_request.py",
    ROOT / "benchmarks" / "latency.py",
    ROOT / "benchmarks" / "concurrency.py",
]


def test_benchmarks_count_reasoning_deltas():
    for script in SCRIPTS:
        text = script.read_text(encoding="utf-8")
        assert script.is_file(), f"{script.name} must exist"
        assert 'delta.get("content")' in text
        assert 'delta.get("reasoning")' in text
        assert 'delta.get("reasoning_content")' in text
