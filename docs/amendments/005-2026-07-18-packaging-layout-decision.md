# Amendment 005: Permanent Python src-Layout Packaging Structure

**Date:** 2026-07-18  
**Type:** Architecture + Packaging  
**Status:** PROPOSED

## Change

Phase 8D.2 confirmed that this repository will use a Python `src`-layout permanently. This amendment supersedes the Section 3 and Section 13 wording that treats `python/src/` as a legacy location or requires migration to a repository-root `core/` directory.

No source-code or packaging configuration changes are made by this amendment. It records the architectural decision for a subsequent Constitution update.

### Existing wording

#### Section 3 — Folder Responsibilities

The current tree places `core/` at repository root:

```text
/root/Projects/Trading-System/
├── core/                    # Generic, market-agnostic infrastructure. Never strategy-specific.
│   ├── data/
│   ├── indicators/
│   ├── models/
│   ├── portfolio/
│   ├── scanner/
│   └── tools/
...
├── python/src/              # Legacy source location — DEPRECATED
│   └── trading_system/       # Will be migrated to core/ in a future refactor
```

#### Section 13 — Current State

> The `python/src/trading_system/` directory is a **legacy location** and is excluded from this constitution until migrated.

### Proposed wording

#### Section 3 — Folder Responsibilities

Replace the root-level `core/` entry and deprecated `python/src/` entry with the following canonical source tree:

```text
/root/Projects/Trading-System/
├── python/
│   └── src/
│       └── core/             # Generic, market-agnostic infrastructure. Never strategy-specific.
│           ├── data/         # Caching, storage, download, validation, retry, session, provider
│           ├── indicators/   # Pure mathematical transforms (MA, normalization, ranking, RS formula)
│           ├── models/       # Generic data structures (Candle, Symbol, MarketData, ScanResult)
│           ├── portfolio/    # Generic risk concepts (allocation, sizing, position, risk, portfolio)
│           ├── scanner/      # Screening framework (pipeline, filters, result) — no signal logic
│           └── tools/        # Analytics, market utilities — no strategy rule implementation
...
├── strategies/              # ISOLATED strategy implementations. One folder per experiment.
```

The Section 3 rules continue to apply to the source-rooted `core/`: it must never import from strategies; strategies must not import from each other; and research outputs must not live inside the source tree.

#### Section 13 — Current State

Replace the legacy statement with:

> `python/src/` is the standard Python source root for this repository and is governed by this Constitution. The source-rooted `python/src/core/` contains generic, market-agnostic infrastructure. It is not a legacy location and is not scheduled for migration to a repository-root `core/` directory.

### New permanent packaging clause

Add the following clause to the Constitution’s packaging or folder-responsibility rules:

> **Permanent src-layout decision:** The repository permanently uses Python `src`-layout. Importable core source resides under `python/src/`; a repository-root `core/` directory is not the target architecture. Any future packaging change must be proposed through a new amendment and must preserve the separation between importable source, strategies, research, configuration, and generated outputs.

## Engineering Rationale

1. **Prevents accidental imports from the repository root.** With a flat layout, the working directory can place an in-development package ahead of the installed package on `sys.path`. Keeping importable code under `python/src/` makes tests and development exercise the installed or editable package rather than an unintended checkout path.
2. **Makes package boundaries explicit.** Repository documentation, configuration, scripts, experiments, and generated outputs remain outside the importable source tree. This reduces accidental package discovery and distribution of unrelated directories.
3. **Aligns the architecture with the existing Python project.** The implementation already lives under `python/src/`, and the project test configuration points Python at `python/src`. Treating that location as canonical avoids a needless repository-wide move and preserves the existing source/test separation.
4. **Preserves the Constitution’s isolation goals.** Moving the conceptual `core/` responsibility below the Python source root changes packaging placement, not ownership: core remains market-agnostic, strategies remain isolated, and research outputs remain outside source directories.
5. **Removes an obsolete migration mandate.** A future move to top-level `core/` would replace a packaging best practice with a flat layout without improving the platform’s mission. The migration language is therefore superseded rather than left ambiguous.

## Source of Decision

### Project decision

- **Phase 8D.2 packaging-layout analysis:** project decision to retain `python/src/` as the canonical and permanent Python `src`-layout source root.
- **Repository evidence:** the current Python implementation is under `python/src/trading_system/`, and `pyproject.toml` configures pytest with `pythonpath = ["python/src"]`.

### External guidance

- Python Packaging User Guide, **“src layout vs flat layout”**: explains that `src`-layout places importable packages below a separate `src/` directory and helps prevent accidental use of the in-development copy of the code.
  - https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/
- Python Packaging User Guide, **“Packaging Python Projects”**: uses a `src/` directory for package source in its packaging tutorial.
  - https://packaging.python.org/en/latest/tutorials/packaging-projects/
- pytest documentation, **“Good Integration Practices — Choosing a test layout”**: generally suggests `src`-layout, especially with the default import mode, and documents testing against installed or editable packages.
  - https://docs.pytest.org/en/latest/explanation/goodpractices.html#tests-outside-application-code
- setuptools documentation, **“Package Discovery — src-layout”**: describes the source-root layout as less error-prone for discovery because unrelated root folders are not included as package content by default.
  - https://setuptools.pypa.io/en/latest/userguide/package_discovery.html#src-layout

## Impact

- Section 3 will describe `python/src/core/`, not a repository-root `core/`, as the location of generic core infrastructure.
- Section 13 will recognize `python/src/` as the standard governed source root rather than excluding it as legacy.
- The proposed permanent clause prevents future work from interpreting the old top-level migration mandate as still active.
- Strategies, research, markets, workspace, configuration, tests, and OpenCode directories retain their existing responsibilities.
- This amendment changes documentation intent only; it does not modify the Constitution or require code changes.

## Supersession and Consistency

Upon approval and incorporation into the Constitution, this amendment supersedes only the conflicting packaging statements in Sections 3 and 13. All other folder responsibilities, dependency rules, testing rules, amendment rules, and isolation requirements remain in force. The Constitution’s `core` dependency rules apply to `python/src/core/` after this amendment.
