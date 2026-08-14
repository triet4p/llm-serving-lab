# Lessons Learned

## [2026-08-14] Documentation tests assert literal command strings, not paraphrases

**Symptom:** In Sprint 4, `test_readme_documents_starting_the_server` failed on the first run even though the README fully described the model-creation flow ("creates the model from the Modelfile ... skipped when the tag already exists").

**Root cause:** The README described the behavior but never contained the literal `ollama create` command. The repo's README tests check for exact strings (`assert "ollama create" in text`), mirroring the vLLM README test pattern where the documented direct command appears verbatim.

**Fix / workaround:** Added the literal command to the README Start-the-server section: `ollama create "$MODEL_NAME" -f servers/ollama/Modelfile`.

**Watch out for:** Whenever a task includes a documentation/README file (e.g. future Sprint 5-7 README/doc tasks), the doc must state the literal command names and flags that the test asserts on — describing what the script does is not sufficient. When writing a doc test for the first time, check the exact terms the README must contain before drafting the doc.
