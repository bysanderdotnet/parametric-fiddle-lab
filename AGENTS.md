# Agent Operating Manual

One tool runs the whole workflow, prints next step every turn:

    ./AGENTS.sh init       # start here; follow output
    ./AGENTS.sh help       # stuck, or unsure which command fits

Trust script over memory: walks setup, scope, verification, progress,
handoff. All state in `.agents/agents.json`, CLI-owned — never hand-edit.

## Project

- Name: Resonant Violin Lab
- Stack: Python, CadQuery, Gmsh, Elmer, Orca Slicer CLI, Optuna
- Purpose: Building a parametric, simulatable, and optimizable design chain for 3D-printed violins, combining geometry, slicing, material, and structural reinforcement.

## Rules

- One feature per session/commit. No drive-by refactors.
- Done = `./AGENTS.sh verify` green. Anything else = "unverified" — say so.
- `AGENTS.sh` / `.agents/agents.py` = harness internals. Usage = `help`,
  not reading or editing source.
- No-go zones: Do not modify `.agents/agents.json` directly. Use `AGENTS.sh` commands.

## Skills

Skills = stored playbooks in `.agents/skills/<name>/SKILL.md`; `init` lists them.

- Task matches a skill → follow playbook, don't improvise.
- Just did recurring multi-step task (deploy, release, migration, codegen)?
  Capture as skill NOW, unprompted — how-to: `.agents/skills/new-skill/SKILL.md`.
  Next session replays it, no re-deriving.

## Style: caveman

All agent output — chat, commits, code comments, logs, docs — max terse.
Drop filler; fragments fine: "Tests green. Lint: 2 unused imports." Exact
paths, commands, numbers; never paraphrase a name. Say once.

Only exception: the product itself (website copy, UI strings, end-user docs).
