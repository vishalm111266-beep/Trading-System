# Architecture Constitution

> Last amended: 2026-07-15
> Status: Active

---

## 1. Mission

This platform is a **strategy-agnostic research environment** for stock market analysis. Its purpose is to provide isolated, reproducible, and disposable research workflows — not to ship production trading strategies.

The platform must:
- Remain useful across any market (Indian, US, or otherwise)
- Allow strategies to be created, tested, and discarded without modifying the core
- Support concurrent experiments without cross-contamination
- Keep generated artifacts (reports, backtest results, plots) out of source directories

---

## 2. Non-Goals

This platform does NOT:
- Execute live trades
- Maintain a production portfolio
- Provide brokerage integration
- Enforce any single strategy, indicator, or market approach
- Serve as a data provider (data sourcing is a per-experiment concern)
- Replace a backtesting framework (backtesting is per-strategy, run in isolation)

---

## 3. Folder Responsibilities

```
/root/Projects/Trading-System/
├── core/                    # Generic, market-agnostic infrastructure. Never strategy-specific.
│   ├── data/                # Caching, storage, download, validation, retry, session, provider
│   ├── indicators/          # Pure mathematical transforms (MA, normalization, ranking, RS formula)
│   ├── models/               # Generic data structures (Candle, Symbol, MarketData, ScanResult)
│   ├── portfolio/            # Generic risk concepts (allocation, sizing, position, risk, portfolio)
│   ├── scanner/              # Screening framework (pipeline, filters, result) — no signal logic
│   └── tools/                # Analytics, market utilities — no strategy rule implementation
│
├── strategies/              # ISOLATED strategy implementations. One folder per experiment.
│   ├── rs-rank-strategy/     # Example experiment: must be fully self-contained
│   └── sma-crossover/        # Another experiment: disposable
│
├── research/                 # Experiment workspace. One subfolder per research session.
│   ├── exp-001-reliance-rs/  # Contains: notes, config, outputs, plots, backtest results
│   └── exp-002-nifty-ema/
│
├── plugins/                  # Optional, explicit extensions to core behavior
│   └── .gitkeep              # Directory marker only
│
├── markets/                  # Market-specific reference data and rules (NOT logic)
│   ├── india/               # NSE/BSE holiday calendars, circuit limits, tax rules (reference only)
│   └── us/                  # NYSE/NASDAQ rules, PDT thresholds, SEC fees (reference only)
│
├── workspace/               # Transient output: generated reports, plots, exports
│   └── .gitkeep             # Directory marker only
│
├── config/                  # Static YAML config for core infrastructure
│   ├── data.yaml
│   └── logging.yaml
│
├── scripts/                 # Automation scripts (smart-push, phone-cleanup)
│
├── tests/                   # Unit tests for core only (NOT for strategies)
│   └── unit/
│
├── docs/                    # This document and other reference docs
│
├── .opencode/               # OpenCode agents, skills, commands (project-level)
│   ├── agents/
│   ├── skills/
│   └── commands/
│
├── python/src/              # Legacy source location — DEPRECATED
│   └── trading_system/       # Will be migrated to core/ in a future refactor
│
├── opencode.json            # OpenCode project config
└── AGENTS.md               # OpenCode root agent routing (project-level, rule-only)
```

### Rules:
- **Core must never import from strategies.**
- **Strategies must never import from each other.**
- **Research outputs must never live inside core or strategies.**
- **Every experiment gets its own folder under `research/`.**
- **Every strategy gets its own folder under `strategies/`.**

---

## 4. Dependency Rules

1. Core has **zero external market data dependencies**. It defines interfaces; data sources are injected.
2. Strategies depend only on core interfaces. They do not depend on each other.
3. Research notebooks or scripts under `research/` may depend on core + exactly one strategy.
4. The `.opencode/` config does not depend on any strategy or research folder.
5. No Python import from `research/` or `strategies/` into `.opencode/` agents.

---

## 5. Plugin Rules

1. Plugins live under `plugins/` and are explicitly registered in `opencode.json`.
2. A plugin must not modify core data models or interfaces.
3. Plugins provide optional capabilities (e.g., alternative data source, custom plotting).
4. Plugins are **opt-in per config**, not auto-loaded.
5. A plugin that introduces a strategy-specific concern will not be accepted.

---

## 6. Market Rules

1. Core contains **no hardcoded market assumptions**.
2. Market-specific parameters (NSE holidays, circuit breakers, PDT thresholds, tax rates) live in `markets/` as reference data only.
3. Agents and skills may reference `markets/` for context, but must not enforce market-specific logic as universal truth.
4. Market detection (Indian vs US) is the **first step** in any analysis workflow and drives ticker suffix normalization (.NS / .BO / standard).

---

## 7. Research Workflow

Every research session follows this lifecycle:

```
1. CREATE    → mkdir research/exp-XXX-name/
2. CONFIG    → Store parameters, ticker, date range in exp-XXX-name/notes.md
3. RUN       → Execute analysis, backtest, or experiment
4. CAPTURE   → Save outputs to exp-XXX-name/outputs/
5. REVIEW    → Human reviews results
6. DISCARD   → Delete entire folder when done, OR promote to strategies/ if proven
```

Rules:
- One experiment per folder.
- Never modify an experiment folder after it is closed.
- Never mix two experiments in one folder.
- Backtest results are **never** in core or source trees.

---

## 8. Workspace Rules

1. All generated files (plots, HTML reports, CSVs, parquet) go to `workspace/`.
2. The `workspace/` directory is never committed to git (it is in `.gitignore`).
3. Files in `workspace/` are never imported by core or strategies.
4. Only research session outputs may use `workspace/`.

---

## 9. Cloud Rules

1. Code lives in Git; data lives in cloud storage (per `smart-push.sh`).
2. The `scripts/smart-push.sh` script enforces separation: code is pushed to Git, local data is cleaned.
3. Git LFS handles large generated files.
4. Cloud sync credentials are never in `opencode.json` or any config file.
5. Research outputs are pushed with code only when explicitly requested.

---

## 10. Testing Rules

1. Tests cover **core only**. Strategies and research are not tested.
2. Unit tests live in `tests/unit/` mirroring the core directory structure.
3. Integration tests exist only for stable core interfaces.
4. No test may depend on a live market data connection.
5. Coverage minimum for core: **50%** (enforced in `pyproject.toml`).
6. Strategies are tested in their own folders, outside `tests/`.

---

## 11. Amendment Rules

1. This document is the **single source of truth** for architecture decisions.
2. Any change to this document requires a new file in `docs/amendments/` named `001-YYYY-MM-DD-brief-description.md`.
3. Amendments are evaluated by the **@architect** agent and approved by the user before merging.
4. No change may violate the mission or non-goals.
5. No change may remove the isolation between core, strategies, and research.
6. This document is versioned in Git. Older versions are never deleted.

---

## 12. Enforcement

- The **@architect** agent is responsible for enforcing this constitution.
- The **@reviewer** agent must flag any PR or change that violates these rules.
- The **@experiment-runner** agent is the only agent authorized to create research folders.
- No agent may move, rename, or delete files in `core/` without user approval.

---

## 13. Current State

- This constitution was created on 2026-07-15.
- The `python/src/trading_system/` directory is a **legacy location** and is excluded from this constitution until migrated.
- The `.opencode/` agents and skills are **reference implementations** and are not yet restructured. They will be updated in later phases.
- The root `AGENTS.md` is **strategy-specific** and will be replaced in Phase 2.