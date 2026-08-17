import json
import subprocess
import sys

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "benchmarks" / "aggregate_report.py"


def _write(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


def test_aggregate_report_reads_nested_layout(tmp_path):
    _write(
        tmp_path / "default" / "single_request" / "baseline" / "single_request_20260101-000000.json",
        {
            "summary": {"total_time": 1.0, "time_to_first_token": 0.1, "generation_time": 0.9, "tokens": 10, "tokens_per_second": 11.1},
            "requests": [{"total_time": 1.0, "time_to_first_token": 0.1, "tokens": 10, "label": "short"}],
        },
    )
    _write(
        tmp_path / "multi-length" / "concurrency" / "vllm" / "concurrency_20260101-000001.json",
        {
            "summary": {"wall_time_s": 5.0, "requests_per_second": 2.0, "tokens_per_second": 100.0, "latency_mean_s": 1.0},
            "requests": [
                {"total_time": 1.0, "time_to_first_token": 0.1, "tokens": 10, "label": "short"},
                {"total_time": 4.0, "time_to_first_token": 0.3, "tokens": 300, "label": "long"},
            ],
        },
    )

    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--results-dir", str(tmp_path)],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    out = proc.stdout

    assert "## default" in out
    assert "## multi-length" in out
    assert "### single_request" in out
    assert "### concurrency" in out
    assert "| baseline |" in out
    assert "| vllm |" in out
    assert "#### by label" in out
    assert "| short |" in out
    assert "| long |" in out


def test_aggregate_report_rejects_missing_dir(tmp_path):
    missing = tmp_path / "nope"
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--results-dir", str(missing)],
        capture_output=True,
        text=True,
    )
    assert proc.returncode != 0
    assert "not found" in proc.stderr
