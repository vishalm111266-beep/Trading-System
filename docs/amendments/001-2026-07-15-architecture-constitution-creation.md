# Amendment: 001-2026-07-15-architecture-constitution-creation

**Date:** 2026-07-15
**Status:** APPROVED

## Change

Created `docs/ARCHITECTURE_CONSTITUTION.md` — the master architecture document defining:
- Mission and non-goals (research platform, not trading system)
- Folder responsibilities with strict ownership rules
- Dependency rules (core ↔ strategies ↔ research isolation)
- Plugin rules
- Market rules (no hardcoded market assumptions)
- Research workflow lifecycle
- Workspace rules (generated outputs → workspace/, not source)
- Cloud rules (smart-push enforcement)
- Testing rules (core only, 50% minimum coverage)
- Amendment rules (documented changes only via `docs/amendments/`)

## Rationale

The repository lacked a governing document that separated:
- Generic infrastructure from strategy-specific code
- Research experiments from production code
- Generated artifacts from source directories

Without this constitution, new code risked becoming entangled with strategy logic.

## Impact

- All future structural changes must reference this document
- Phase 1 of the platform restructuring is now complete
- 9 subsequent phases remain (2-10) to fully migrate the codebase