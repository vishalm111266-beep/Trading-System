# DECISIONS.md

Architectural Decision Records (ADRs) for the Trading System.

Format: One record per decision. Most recent first.

---

## ADR-001: Phone-First Architecture

**Date:** 2026-07-14
**Status:** Accepted
**Context:** The system must be accessible and functional on a mobile device without requiring a desktop or cloud infrastructure.
**Decision:** All components will target Android + Termux + Ubuntu Proot as the primary runtime environment.
**Consequences:**
- All tooling must be CLI-based
- No GUI dependencies allowed
- Resource usage must be bounded (RAM, CPU, storage)
- Testing must verify Proot compatibility

---

## ADR-002: Local-First Data Storage

**Date:** 2026-07-14
**Status:** Accepted
**Context:** Market data must be available offline and reliably retrievable for backtesting and analysis.
**Decision:** All fetched data will be stored locally in structured formats (SQLite/Parquet). No runtime dependency on external data services.
**Consequences:**
- Data fetching is a separate, scheduled concern
- Storage management and cleanup policies are required
- Initial data backfill takes time but subsequent runs are fast
- Data integrity checks must run on load

---

## ADR-003: No Trading Strategy Logic

**Date:** 2026-07-14
**Status:** Accepted
**Context:** The system is a research workspace, not a trading execution platform. Strategy logic belongs in the operator's decision process.
**Decision:** The system will not contain, suggest, or implement trading strategies. It provides data, analysis, and backtesting infrastructure only.
**Consequences:**
- Clean separation between tooling and strategy
- No automated trade execution code
- Backtesting framework is strategy-agnostic
- Documentation must not include strategy examples

---

## ADR-004: Modular Directory Structure

**Date:** 2026-07-14
**Status:** Accepted
**Context:** The system spans multiple languages (Python, Pine Script, Shell) and concerns (data, research, backtesting). A clear module boundary prevents coupling.
**Decision:** Each top-level directory is an independent module with a single responsibility. Cross-module communication happens through well-defined interfaces.
**Consequences:**
- Easy to navigate and understand
- Independent development of modules
- Clear ownership of code and data
- Risk of over-fragmentation if too many small modules are created

---

## ADR-005: Python as Primary Language

**Date:** 2026-07-14
**Status:** Accepted
**Context:** The system needs a language with strong data processing libraries, good CLI support, and availability in Proot Ubuntu.
**Decision:** Python 3.10+ is the primary language for backtesting, data processing, and analysis. Pine Script v5 is used for TradingView indicators.
**Consequences:**
- stdlib preference over third-party libraries where possible
- Type hints required for maintainability
- All dependencies must be pip-installable in Proot
- Pine Script remains separate in `pine/` directory
