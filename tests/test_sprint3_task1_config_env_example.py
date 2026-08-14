from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "servers" / "vllm" / "config.env.example"


def config_text() -> str:
    return CONFIG.read_text(encoding="utf-8")


def test_config_env_example_exists():
    assert CONFIG.is_file(), "servers/vllm/config.env.example must exist"


def test_config_documents_model():
    assert "MODEL_NAME" in config_text()
    assert "Qwen/Qwen3-8B" in config_text()


def test_config_documents_host_and_port():
    assert "HOST" in config_text()
    assert "0.0.0.0" in config_text()
    assert "PORT" in config_text()
    assert "8000" in config_text()


def test_config_documents_tensor_parallel():
    assert "TENSOR_PARALLEL_SIZE" in config_text()
