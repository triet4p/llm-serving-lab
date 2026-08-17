import json

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATASETS = ROOT / "benchmarks" / "datasets"
SCRIPTS = [
    ROOT / "benchmarks" / "single_request.py",
    ROOT / "benchmarks" / "latency.py",
    ROOT / "benchmarks" / "concurrency.py",
]


def test_multi_length_dataset_exists_and_valid():
    path = DATASETS / "multi-length.json"
    assert path.is_file(), "benchmarks/datasets/multi-length.json must exist"
    data = json.loads(path.read_text(encoding="utf-8"))
    labels = {req.get("label") for req in data["requests"]}
    assert "short" in labels and "long" in labels
    assert any(r.get("max_tokens", 0) >= 512 for r in data["requests"])


def test_benchmarks_offer_dataset_flag():
    for script in SCRIPTS:
        text = script.read_text(encoding="utf-8")
        assert script.is_file(), f"{script.name} must exist"
        assert '--dataset' in text
        assert "datasets/<name>.json" in text
        assert "load_dataset(" in text


def test_latency_and_concurrency_report_per_label():
    for name in ("latency.py", "concurrency.py"):
        text = (ROOT / "benchmarks" / name).read_text(encoding="utf-8")
        assert "per-label summary" in text


def test_single_request_filters_by_label():
    text = (ROOT / "benchmarks" / "single_request.py").read_text(encoding="utf-8")
    assert "--label" in text
