# AGENTS.md

## Global rules and skills

Before working, load and follow the shared rules and skills located outside this repo:

- Rules: `~/.agents/rules` (e.g. `python.md`, `shell.md`, `git.md`, `markdown.md`, `changelog.md`)
- Skills: `~/.agents/skills` (available skills are also listed by the opencode skill tool)

Use the skill loader when a task matches an available skill.

## Project memory

Before working, read the append-only memory logs and follow any decisions or lessons recorded there:

- Decisions: `.agents/memory/decisions.md` — deliberate choices (library picks, API contracts, trade-offs) that must not be reversed without explicit instruction.
- Lessons learned: `.agents/memory/lessons-learned.md` — bugs, quirks, and non-obvious traps discovered in this repo.

When a task matches, log new entries per the `log-decision` and `log-lesson` skills.

## Project state

This repository is in the planning phase: `docs/` contains the design documents and nothing else.

- No application code, dependencies, build/test tooling, or CI exist yet.
- There is no `README.md`, no manifests, and no developer commands to run.
- Do not assume files referenced by the docs exist (e.g. `servers/`, `clients/`, `benchmarks/`).

## Source of truth

- Read `docs/01-project-concept-overview.md` through `docs/04-project-technical-stack.md` before building anything.
- These docs define the intended architecture: serving backends and clients are separated, clients use a single compatible API contract, and the project must stay simple and demo-friendly.
- When creating code or structure, follow the planned layout in `docs/02-project-architecture.md`; where code conflicts with docs, code wins but flag the discrepancy.
