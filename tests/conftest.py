from pathlib import Path

import pytest


@pytest.fixture
def load_env():
    def _load(rel_path: str) -> dict[str, str]:
        path = Path(__file__).resolve().parents[1] / rel_path
        assert path.is_file(), f"missing file: {rel_path}"
        env: dict[str, str] = {}
        for raw in path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            key, _, value = line.partition("=")
            env[key.strip()] = value.strip()
        return env

    return _load
