from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TOP_LEVEL_DIRS = [
    "servers",
    "clients",
    "benchmarks",
    "configs",
    "profiles",
    "scripts",
    "slides",
]


def test_top_level_dirs_exist():
    for name in TOP_LEVEL_DIRS:
        assert (ROOT / name).is_dir(), f"missing directory: {name}/"


def test_empty_dirs_have_gitkeep():
    empty_dirs = ["servers", "clients", "benchmarks", "slides"]
    for name in empty_dirs:
        assert (ROOT / name / ".gitkeep").is_file(), f"missing .gitkeep in {name}/"
