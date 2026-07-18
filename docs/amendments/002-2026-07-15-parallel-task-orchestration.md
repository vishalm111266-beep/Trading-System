# Amendment 002: Parallel Task Orchestration

**Date:** 2026-07-15
**Type:** OpenCode Configuration

## Summary

Added parallel task-orchestration system with primary orchestrator agent, four subagents, and custom parallel command.

## Changes

### New Files

1. `.opencode/agents/orchestrator.md` — Primary orchestrator agent (mode: primary)
2. `.opencode/agents/implementer.md` — Implementation subagent (replaces coder for orchestration)
3. `.opencode/commands/parallel.md` — Custom parallel command

### Updated Files

1. `.opencode/agents/researcher.md` — Clearer read-only permissions
2. `.opencode/agents/reviewer.md` — Clearer read-only permissions
3. `.opencode/agents/tester.md` — Limited bash permissions
4. `opencode.json` — Added default_agent and model_overrides

## Architecture

```
@orchestrator (primary, default)
├── @researcher — read-only research
├── @implementer — approved code changes only
├── @reviewer — read-only quality review
└── @tester — bash for tests only
```

## Branch Types

| Type | Agent | Tools |
|------|-------|-------|
| research | @researcher | read, glob, grep, webfetch, websearch |
| implement | @implementer | edit, write (approved branches only) |
| review | @reviewer | read, glob, grep, bash (verification) |
| test | @tester | bash (pytest only) |

## Parallel Command

```
/parallel [request]
```

Triggers orchestrator to split work into independent branches.

## Rules

1. Only split truly independent work
2. Do not parallelize dependent steps
3. Prefer 3 branches over 10
4. If one agent can do it faster, do not parallelize
5. Highest-value branch first