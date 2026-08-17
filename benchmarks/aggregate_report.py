#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# ///
"""Aggregate benchmark results into a markdown report.

Reads the results tree <results>/<dataset>/<type>/<backend>/<type>_<timestamp>.json
(flat files are also accepted), groups by dataset/type/backend, and prints a
comparison report: one backend table per benchmark type per dataset, plus a
per-label breakdown (e.g. short/medium/long) built from the per-request rows.

Usage:

    uv run benchmarks/aggregate_report.py
    uv run benchmarks/aggregate_report.py --results-dir benchmarks/results
    uv run benchmarks/aggregate_report.py --output benchmarks/results/report.md
"""

import argparse
import json
import statistics
import time
from pathlib import Path

TYPES = ("single_request", "latency", "concurrency")


def mean(values: list) -> float:
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


def collect(results_dir: Path) -> dict[str, dict[str, dict[str, list]]]:
    """Return dataset -> type -> backend -> list of (path, json) runs."""
    tree: dict[str, dict[str, dict[str, list]]] = {}
    for path in sorted(results_dir.rglob("*.json")):
        bench_type = next(
            (t for t in TYPES if path.name.startswith(t + "_")), None
        )
        if bench_type is None:
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        parts = path.relative_to(results_dir).parts
        dataset = parts[0] if len(parts) >= 2 else "root"
        backend = parts[-2] if len(parts) >= 2 else "root"
        tree.setdefault(dataset, {}).setdefault(bench_type, {}).setdefault(
            backend, []
        ).append((path, data))
    return tree


def render_type(bench_type: str, backends: dict[str, list]) -> str:
    lines = [f"### {bench_type}", ""]
    if not backends:
        lines.append("_no results_")
        lines.append("")
        return "\n".join(lines)

    sample = run_metrics(bench_type, next(iter(backends.values()))[0][1].get("summary", {}))
    columns = list(sample.keys())
    lines.append("| backend | runs | " + " | ".join(columns) + " |")
    lines.append("|" + "---|" * (len(columns) + 2))
    for backend in sorted(backends):
        runs = backends[backend]
        rows = [run_metrics(bench_type, run.get("summary", {})) for _, run in runs]
        cells = [backend, str(len(runs))] + [
            fmt(mean([r.get(c) for r in rows])) for c in columns
        ]
        lines.append("| " + " | ".join(cells) + " |")
    lines.append("")

    labels: dict[tuple[str, str], list[tuple[float, float, float]]] = {}
    for backend in backends:
        for _, run in backends[backend]:
            for row in run.get("requests", []):
                label = row.get("label") or "default"
                labels.setdefault((backend, label), []).append(
                    (
                        row.get("total_time", 0.0),
                        row.get("time_to_first_token", 0.0),
                        row.get("tokens", 0.0),
                    )
                )
    if any(label != "default" for _, label in labels):
        lines.append("#### by label")
        lines.append("")
        lines.append("| backend | label | n | mean_total_s | mean_ttft_s | mean_tokens |")
        lines.append("|---|---|---|---|---|---|")
        for (backend, label) in sorted(labels):
            vals = labels[(backend, label)]
            lines.append(
                f"| {backend} | {label} | {len(vals)} | "
                f"{fmt(mean([v[0] for v in vals]))} | "
                f"{fmt(mean([v[1] for v in vals]))} | "
                f"{fmt(mean([v[2] for v in vals]))} |"
            )
        lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Aggregate benchmark results into a report")
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

    tree = collect(results_dir)
    header = [
        "# Benchmark Aggregation Report",
        f"- results dir: {results_dir}",
        f"- generated: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        "",
    ]
    if not tree:
        header.append("_no benchmark results found_")
        header.append("")
    for dataset in sorted(tree):
        header.append(f"## {dataset}")
        header.append("")
        for bench_type in TYPES:
            if bench_type in tree[dataset]:
                header.append(render_type(bench_type, tree[dataset][bench_type]))
    report = "\n".join(header)

    print(report)
    if args.output:
        Path(args.output).write_text(report + "\n", encoding="utf-8")
        print(f"saved: {args.output}")


if __name__ == "__main__":
    main()
