import pytest


@pytest.mark.parametrize(
    "profile",
    ["baseline", "vllm", "ollama"],
)
def test_profile_defines_contract_vars(load_env, profile):
    env = load_env(f"profiles/{profile}.env")
    for var in ("OPENAI_BASE_URL", "OPENAI_API_KEY", "MODEL_NAME"):
        assert var in env, f"missing {var} in profiles/{profile}.env"
        assert env[var], f"empty value for {var} in profiles/{profile}.env"
    assert env["OPENAI_BASE_URL"].startswith("http")
    assert env["OPENAI_BASE_URL"].endswith("/v1")
