# LLM Serving Lab - convenience commands
#
# Each target sources the shared model config plus the matching backend
# profile, exporting OPENAI_BASE_URL / OPENAI_API_KEY / MODEL_NAME so that
# later servers, clients, and scripts can rely on the same contract.
#
# Targets:
#   make serve-baseline   start the baseline FastAPI server
#   make serve-vllm       start the vLLM server
#   make serve-ollama     start the Ollama server
#   make smoke            run the smoke test against the active backend
#   make benchmark        run benchmarks against the active backend
#   make health           check the active backend's health endpoint
#
# PROFILE selects the backend used by smoke/benchmark/health (default: vllm).
#   make smoke PROFILE=ollama

SHELL := /bin/bash
PROFILE ?= vllm

.PHONY: serve-baseline serve-vllm serve-ollama smoke benchmark health

# Load the shared default model plus a backend profile and export the vars.
define load_profile
set -a; \
source configs/models.env; \
source profiles/$(1).env; \
set +a
endef

serve-baseline:
	$(call load_profile,baseline); \
	echo "==> Starting baseline FastAPI server (OPENAI_BASE_URL=$$OPENAI_BASE_URL, MODEL_NAME=$$MODEL_NAME)"; \
	echo "    Runner implemented in Sprint 2."

serve-vllm:
	$(call load_profile,vllm); \
	echo "==> Starting vLLM server (OPENAI_BASE_URL=$$OPENAI_BASE_URL, MODEL_NAME=$$MODEL_NAME)"; \
	echo "    Runner implemented in Sprint 3."

serve-ollama:
	$(call load_profile,ollama); \
	echo "==> Starting Ollama server (OPENAI_BASE_URL=$$OPENAI_BASE_URL, MODEL_NAME=$$MODEL_NAME)"; \
	echo "    Runner implemented in Sprint 4."

smoke:
	$(call load_profile,$(PROFILE)); \
	echo "==> Smoke test against $$OPENAI_BASE_URL (MODEL_NAME=$$MODEL_NAME)"; \
	echo "    Script implemented in Sprint 5."

benchmark:
	$(call load_profile,$(PROFILE)); \
	echo "==> Benchmark against $$OPENAI_BASE_URL (MODEL_NAME=$$MODEL_NAME)"; \
	echo "    Script implemented in Sprint 6."

health:
	$(call load_profile,$(PROFILE)); \
	echo "==> Healthcheck for $$OPENAI_BASE_URL"; \
	echo "    Script implemented in Sprint 7."
