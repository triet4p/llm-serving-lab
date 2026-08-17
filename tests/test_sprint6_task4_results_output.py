from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = [
    ROOT / "benchmarks" / "single_request.py",
    ROOT / "benchmarks" / "latency.py",
    ROOT / "benchmarks" / "concurrency.py",
]
RESULTS_DIR = ROOT / "benchmarks" / "results"


def test_results_directory_exists():
    assert RESULTS_DIR.is_dir(), "benchmarks/results/ directory must exist"
    assert (RESULTS_DIR / ".gitkeep").is_file(), "benchmarks/results/.gitkeep must exist"


def test_results_directory_is_gitignored():
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert "benchmarks/results/" in gitignore


def test_all_benchmarks_save_json_results():
    for script in SCRIPTS:
        text = script.read_text(encoding="utf-8")
        assert script.is_file(), f"{script.name} must exist"
        assert "json.dumps" in text
        assert ".json" in text
        assert "results_dir" in text or "results" in text


def test_all_benchmarks_save_csv_results():
    for script in SCRIPTS:
        text = script.read_text(encoding="utf-8")
        assert "csv.DictWriter" in text, f"{script.name} must write CSV results"


def test_all_benchmarks_write_into_results_dir():
    for script in SCRIPTS:
        text = script.read_text(encoding="utf-8")
        assert 'Path(__file__).resolve().parent / "results"' in text


def test_all_benchmarks_support_no_save_flag():
    for script in SCRIPTS:
        text = script.read_text(encoding="utf-8")
        assert "--no-save" in text, f"{script.name} must support --no-save"


def test_all_benchmarks_keep_inline_metadata_and_env_contract():
    for script in SCRIPTS:
        text = script.read_text(encoding="utf-8")
        assert "uv run --script" in text
        assert '"httpx' in text
        for var in ("OPENAI_BASE_URL", "OPENAI_API_KEY", "MODEL_NAME"):
            assert var in text, f"{script.name} must read env var: {var}"
