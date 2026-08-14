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
