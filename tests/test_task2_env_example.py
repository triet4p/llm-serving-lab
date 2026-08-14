import pytest


def test_env_example_has_required_vars(load_env):
    env = load_env(".env.example")
    for var in ("OPENAI_BASE_URL", "OPENAI_API_KEY", "MODEL_NAME"):
        assert var in env, f"missing variable {var} in .env.example"
        assert env[var], f"empty value for {var} in .env.example"


def test_env_example_values_are_sane(load_env):
    env = load_env(".env.example")
    assert env["OPENAI_BASE_URL"].startswith("http")
    assert env["OPENAI_BASE_URL"].endswith("/v1")
    assert env["OPENAI_API_KEY"]
    assert env["MODEL_NAME"]
