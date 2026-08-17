#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# ///
"""Aggregate benchmark results into a per-type report.

Scans a results directory for the three benchmark types
(`single_request_*.json`, `latency_*.json`, `concurrency_*.json`), groups them
by type, and prints an aggregated markdown report. Works with any dataset:
per-request rows that carry a `label` (e.g. the multi-length dataset's
short/medium/long prompts) are also aggregated per label.

Usage:

    uv run benchmarks/aggregate_report.py
    uv run benchmarks/aggregate_report.py --results-dir results/multi-length
    uv run benchmarks/aggregate_report.py --output report.md
"""

import argparse
import json
import statistics
import time
from pathlib import Path

TYPES = ("single_request", "latency", "concurrency")


def collect_runs(results_dir: Path, bench_type: str) -> list[tuple[Path, dict]]:
    runs = []
    for path in sorted(results_dir.glob(f"{bench_type}_*.json")):
        try:
            runs.append((path, json.loads(path.read_text(encoding="utf-8"))))
        except json.JSONDecodeError:
            continue
    return runs


def mean(values: list[float]) -> float:
    return statistics.fmean(values) if values else float("nan")


def fmt(value) -> str:
    if value is None:
        return "n/a"
    try:
        f = float(value)
    except (TypeError, ValueError):
        return "n/a"
    return "n/a" if f != f else f"{f:.3f}"


def run_metrics(bench_type: str, summary: dict) -> dict[str, float]:
    if bench_type == "single_request":
        return {
            "total_s": summary.get("total_time"),
            "ttft_s": summary.get("time_to_first_token"),
            "gen_s": summary.get("generation_time"),
            "tokens": summary.get("tokens"),
            "tok_s": summary.get("tokens_per_second"),
        }
    if bench_type == "latency":
        total = summary.get("total_latency_s", {})
        ttft = summary.get("time_to_first_token_s", {})
        return {
            "mean_total_s": total.get("mean"),
            "p50_total_s": total.get("p50"),
            "p95_total_s": total.get("p95"),
            "mean_ttft_s": ttft.get("mean"),
            "tokens_mean": summary.get("tokens_mean"),
        }
    if bench_type == "concurrency":
        return {
            "wall_s": summary.get("wall_time_s"),
            "req_s": summary.get("requests_per_second"),
            "tok_s": summary.get("tokens_per_second"),
            "lat_mean_s": summary.get("latency_mean_s"),
        }
    return {}


def per_label(runs: list[tuple[Path, dict]]) -> dict[str, list[dict]]:
    groups: dict[str, list[dict]] = {}
    for _, run in runs:
        for row in run.get("requests", []):
            groups.setdefault(row.get("label") or "default", []).append(row)
    return groups


def render_type(results_dir: Path, bench_type: str) -> str:
    runs = collect_runs(results_dir, bench_type)
    lines = [f"## {bench_type} ({len(runs)} run{'s' if len(runs) != 1 else ''})", ""]
    if not runs:
        lines.append("_no results_")
        lines.append("")
        return "\n".join(lines)

    metrics = run_metrics(bench_type, runs[0][1].get("summary", {}))
    columns = list(metrics.keys())
    lines.append("| file | " + " | ".join(columns) + " |")
    lines.append("|" + "---|" * (len(columns) + 1))
    for path, run in runs:
        values = run_metrics(bench_type, run.get("summary", {}))
        cells = [path.name] + [fmt(values.get(c)) for c in columns]
        lines.append("| " + " | ".join(cells) + " |")
    lines.append("")

    aggregates = {
        c: mean([run_metrics(bench_type, run.get("summary", {}))[c] for _, run in runs])
        for c in columns
    }
    agg_cells = " | ".join(fmt(aggregates[c]) for c in columns)
    lines.append(f"**aggregate (mean):** | {agg_cells} |")
    lines.append("")

    labels = per_label(runs)
    if any(key != "default" for key in labels):
        lines.append("### by label")
        lines.append("")
        lines.append("| label | n | mean_total_s | mean_ttft_s | mean_tokens |")
        lines.append("|---|---|---|---|---|")
        for label in sorted(labels):
            rows = labels[label]
            total = mean([r.get("total_time", 0.0) for r in rows])
            ttft = mean([r.get("time_to_first_token", 0.0) for r in rows])
            toks = mean([r.get("tokens", 0.0) for r in rows])
            lines.append(
                f"| {label} | {len(rows)} | {fmt(total)} | {fmt(ttft)} | {fmt(toks)} |"
            )
        lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Aggregate benchmark results by type")
    parser.add_argument(
        "--results-dir",
        default=str(Path(__file__).resolve().parent / "results"),
        help="directory with benchmark result JSON files (default: benchmarks/results/)",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="also write the report to this file",
    )
    args = parser.parse_args()

    results_dir = Path(args.results_dir)
    if not results_dir.is_dir():
        raise SystemExit(f"results dir not found: {results_dir}")

    header = [
        "# Benchmark Aggregation Report",
        f"- results dir: {results_dir}",
        f"- generated: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        "",
    ]
    sections = [render_type(results_dir, t) for t in TYPES]
    report = "\n".join(header + sections)

    print(report)
    if args.output:
        Path(args.output).write_text(report + "\n", encoding="utf-8")
        print(f"saved: {args.output}")


if __name__ == "__main__":
    main()
