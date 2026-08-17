# Lessons Learned

## [2026-08-14] Documentation tests assert literal command strings, not paraphrases

**Symptom:** In Sprint 4, `test_readme_documents_starting_the_server` failed on the first run even though the README fully described the model-creation flow ("creates the model from the Modelfile ... skipped when the tag already exists").

**Root cause:** The README described the behavior but never contained the literal `ollama create` command. The repo's README tests check for exact strings (`assert "ollama create" in text`), mirroring the vLLM README test pattern where the documented direct command appears verbatim.

**Fix / workaround:** Added the literal command to the README Start-the-server section: `ollama create "$MODEL_NAME" -f servers/ollama/Modelfile`.

**Watch out for:** Whenever a task includes a documentation/README file (e.g. future Sprint 5-7 README/doc tasks), the doc must state the literal command names and flags that the test asserts on — describing what the script does is not sufficient. When writing a doc test for the first time, check the exact terms the README must contain before drafting the doc.

## [2026-08-14] Marking a sprint complete requires updating docs/PLAN.md, not just the sprint plan

**Symptom:** After implementing all Sprint 5 tasks I marked every task `[x]` in `docs/sprint-plans/sprint-5.md` but left `docs/PLAN.md` showing "Sprint 5 - Status: Not Started" and Milestone 3 unchecked, so the project plan was stale and misleading.

**Root cause:** I treated the sprint plan file as the only place that tracks completion and missed the established convention: when a sprint finishes, PLAN.md must be updated too (milestone checkbox, Active Sprints status, and a line in Completed Sprints). The convention is visible in commit `931751d docs: mark sprint 1 complete`, which updated README + PLAN.md together with the sprint plans.

**Fix / workaround:** Update `docs/PLAN.md` in the same pass as marking sprint tasks done: tick the matching milestone `- [x]`, flip the sprint's status from "Not Started" to "Complete" in Active Sprints, and add it to the Completed Sprints list.

**Watch out for:** Sprint completion is a two-file change. After finishing the last atomic task of any sprint, always update `docs/PLAN.md` (milestone + status + completed list) alongside `docs/sprint-plans/sprint-<n>.md`, and mention PLAN.md in the commit message (e.g. `docs: mark sprint <n> complete`).

## [2026-08-17] End the benchmark server process after each SSH benchmark run

**Symptom:** After benchmarking the baseline FastAPI server (started via SSH), the uvicorn process stayed alive holding the GPU model in memory; the next backend's benchmark would then contend for GPU memory, or an accidental warm-up request would re-trigger a slow model load in the wrong server instance.

**Root cause:** A server started in the background with `nohup ... &` keeps running after the SSH session ends. Each benchmark cycle leaves a stale serving process behind unless it is explicitly killed.

**Fix / workaround:** After running each benchmark, kill the server process on the GPU server, e.g. `pkill -f '[u]vicorn app:app'` (the `[u]` bracket avoids `pkill` matching its own invoking shell). Verify with `ss -tlnp | grep <port>` that the port is free before starting the next backend.

**Watch out for:** Any benchmark/demo cycle that starts a server over SSH. Leaving the previous backend running is the default, not the exception; make "stop the server" an explicit step between backends.

## [2026-08-17] vLLM engine init fails on CUDA 13 + GCC > 12 (flashinfer JIT)

**Symptom:** `vllm serve` aborted during engine init with `RuntimeError: Engine core initialization failed`; the log showed `error: -- unsupported GNU version! gcc versions later than 12 are not supported!` and, after bypassing that, `identifier "_Float32" is undefined`, from a `ninja` build of `flashinfer/data/csrc/renorm.cu`.

**Root cause:** The server's CUDA 13.0 nvcc only supports host GCC <= 12, but the default is GCC 13.2 (Ubuntu). vLLM triggers flashinfer's runtime JIT kernel build on first start, which invokes nvcc against the new headers and fails.

**Fix / workaround:** In `servers/vllm/run.sh`, route the host compilers to GCC 12 before launching: `export CC=/usr/bin/gcc-12`, `export CXX=/usr/bin/g++-12`, `export NVCC_PREPEND_FLAGS="-ccbin=/usr/bin/g++-12"`. `-allow-unsupported-compiler` alone is NOT enough — the compile still fails on `_Float32`.

**Watch out for:** Any machine with CUDA 13.x whose default GCC is newer than 12. First vLLM start JIT-compiles flashinfer ops and can take several minutes before the API is ready; poll `/v1/models`, don't assume a crash.
