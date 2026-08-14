import pytest


def test_models_env_defines_model(load_env):
    env = load_env("configs/models.env")
    assert env.get("MODEL_NAME"), "configs/models.env must define MODEL_NAME"


def test_endpoints_env_defines_all_backends(load_env):
    env = load_env("configs/endpoints.env")
    for var in ("BASELINE_BASE_URL", "VLLM_BASE_URL", "OLLAMA_BASE_URL"):
        assert var in env, f"missing {var} in configs/endpoints.env"
        assert env[var].startswith("http"), f"{var} must start with http"
        assert env[var].endswith("/v1"), f"{var} must end with /v1"
