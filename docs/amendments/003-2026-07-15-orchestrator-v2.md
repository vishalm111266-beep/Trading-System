# Amendment 003: Orchestrator v2 Architecture

**Date:** 2026-07-15
**Type:** Configuration Update
**Status:** APPROVED & IMPLEMENTED

## Change Summary

Upgraded OpenCode orchestrator to v2 architecture with:

1. **New agent files** in `.opencode/agents/`:
   - `orchestrator.md` - Pure router (edit:deny, task:allow)
   - `researcher.md` - Technical research subagent
   - `implementer.md` - Feature implementation subagent
   - `reviewer.md` - Code review subagent
   - `tester.md` - Test verification subagent

2. **New skills** in `.opencode/skills/`:
   - `task-splitter/` - Dependency analysis for parallel execution
   - `code-review/` - Structured review checklist
   - `research-intake/` - Structured research workflow

3. **Updated `opencode.json`**:
   - Added `compaction` config with auto-prune
   - Added `skills.paths` configuration
   - Enhanced `agent.*` descriptions and mode declarations

4. **Updated `AGENTS.md`**:
   - Added Orchestrator Rules section
   - Updated Routing Table with orchestrator
   - Added orchestration workflow

## Rationale

- Pure router pattern prevents orchestrator from executing directly
- Parallel execution requires multiple task calls in single message
- Compaction prevents unbounded context growth
- Skills provide reusable workflow patterns

## Compatibility

- All changes are additive or config-only
- Existing agents preserved (now also have .md files)
- Rollback: revert opencode.json, AGENTS.md, delete new files

## Rollback Procedure

```bash
git checkout HEAD~1 -- opencode.json AGENTS.md
rm -rf .opencode/agents/orchestrator.md .opencode/agents/researcher.md .opencode/agents/implementer.md .opencode/agents/reviewer.md .opencode/agents/tester.md
rm -rf .opencode/skills/task-splitter .opencode/skills/code-review .opencode/skills/research-intake
```