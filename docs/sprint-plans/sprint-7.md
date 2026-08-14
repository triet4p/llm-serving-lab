# Sprint 7 Plan

## Sprint Goal
Wire everything together with automation scripts, agent integrations, and demo slides.

## Atomic Tasks
Status legend: [ ] pending / [~] in progress / [x] done

- [ ] Task 1: Create `scripts/healthcheck.sh` that checks backend endpoint health.
- [ ] Task 2: Create `scripts/smoke-test.sh` that sends a smoke-test request to a backend.
- [ ] Task 3: Create `scripts/demo.sh` that orchestrates the demo flow (start backend, healthcheck, smoke, benchmark).
- [ ] Task 4: Add `clients/agents/codex/` integration config pointing a coding agent at the self-hosted endpoint.
- [ ] Task 5: Add `clients/agents/claude-code/` integration config pointing an agent at the self-hosted endpoint.
- [ ] Task 6: Create the `slides/` content describing the serving architecture and learning story.

## Notes / Blockers
- Agent compatibility depends on the specific client/protocol (docs 02 §5).
- Slides may be filled in later; this sprint creates the skeleton.
