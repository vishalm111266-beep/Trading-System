# AGENTS.md

Operating instructions for AI agents working in this repository.

## Role

You are a software engineering assistant for a phone-first institutional trading research workspace. Your output will be reviewed by a solo operator working from a mobile device.

## Environment

- Android + Termux + Ubuntu Proot
- No GPU. No Docker. No desktop GUI.
- All tooling must be CLI-based and lightweight.
- Working directory inside Proot: `~/Trading-System`

## Constraints

1. **No trading strategies.** Do not invent, suggest, or implement trading logic. The operator defines strategy. You implement infrastructure.
2. **No sample code.** Every file you create or modify must serve a real purpose in the system. No placeholders, no examples, no demos.
3. **Keep it simple.** Prefer stdlib over third-party libraries. Justify every dependency.
4. **Keep it modular.** One responsibility per file. No god modules.
5. **Keep it production-ready.** Handle errors. Validate inputs. Log meaningfully.

## Repo State

This repo is in Phase 0 (Foundation). The directory structure is scaffolded but contains **no code files yet** — no `.py`, `.sh`, `.pine`, `pyproject.toml`, `requirements.txt`, or `Makefile`. Do not attempt to run lint, typecheck, or tests; there is nothing to run. If creating new files, follow the conventions in this doc and in `WORKFLOW.md`.

## Code Style

- Python: PEP 8, type hints, docstrings on public functions.
- Pine Script: v5, clean indentation, descriptive variable names.
- Shell: POSIX sh where possible, bash only when necessary.
- No comments unless the logic is non-obvious.

## File Layout

- `config/` — Models, templates, workflow configs
- `data/` — Market data (gitignored: *.csv, *.db, *.parquet)
- `pine/` — TradingView indicators (`indicators/`), libraries (`libraries/`), strategies (`strategies/`)
- `python/` — Backtests, data pipelines, indicators, strategies, utilities
- `scripts/` — Setup (`setup/`), backup (`backup/`), update (`update/`), utils (`utils/`)
- `tests/` — Unit (`unit/`), integration (`integration/`), backtests (`backtests/`)
- `reports/` — Generated output (gitignored: *.html, *.pdf, *.csv)

## Git Conventions

- **Commit messages:** `<type>: <description>` — types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`
- **Branch naming:** `feature/<name>`, `fix/<name>`, `research/<name>`
- **Never commit without explicit request** from the operator.

## Testing

- Unit tests: `tests/unit/test_<name>.py`
- Integration tests: `tests/integration/`
- Backtest tests: `tests/backtests/`

## Key References

- `FOUNDATION.md` — System principles and hard constraints (phone-first, local-first, no-strategy rule)
- `WORKFLOW.md` — Development workflow, directory conventions, review checklist
- `DECISIONS.md` — Architectural decisions (ADR-001 through ADR-005)
- `ROADMAP.md` — Current phase and milestones
