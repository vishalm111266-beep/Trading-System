# Phase 2 Research: OpenCode AI Engineering Workspace

**Date:** 2026-07-15
**Source:** https://opencode.ai/docs (verified 2026-07-15)

---

## 1. SUPPORTED Features

### Agents

| Feature | Status | Notes |
|---------|--------|-------|
| Primary agents | ✅ Supported | `mode: "primary"`, built-in: build, plan |
| Subagents | ✅ Supported | `mode: "subagent"`, built-in: general, explore, scout |
| File-based agents | ✅ Supported | `.opencode/agents/<name>.md` |
| Inline agents | ✅ Supported | `agent` in opencode.json |
| Agent permissions | ✅ Supported | Per-agent permission overrides |
| Hidden agents | ✅ Supported | `hidden: true` for subagents |
| Task permissions | ✅ Supported | Control subagent invocation |
| Built-in agents | ✅ Supported | build, plan, general, explore, scout, compaction, title, summary |

**Agent File Location:** `.opencode/agents/<name>.md` (NOT `agent/` singular)

### Commands

| Feature | Status | Notes |
|---------|--------|-------|
| File-based commands | ✅ Supported | `.opencode/commands/<name>.md` |
| Inline commands | ✅ Supported | `command` in opencode.json |
| Arguments (`$ARGUMENTS`, `$1`, `$2`) | ✅ Supported | Placeholder replacement |
| Shell output injection (`` !`command` ``) | ✅ Supported | Bash output in prompts |
| File references (`@file`) | ✅ Supported | Include file content |
| Agent override | ✅ Supported | `agent` field in command |
| Subtask mode | ✅ Supported | `subtask: true` forces subagent |

**Command File Location:** `.opencode/commands/<name>.md` (NOT `command/` singular)

### Skills

| Feature | Status | Notes |
|---------|--------|-------|
| File-based skills | ✅ Supported | `.opencode/skills/<name>/SKILL.md` |
| Global skills | ✅ Supported | `~/.config/opencode/skills/` |
| External skill paths | ✅ Supported | `skills.paths` in opencode.json |
| Skill URLs | ✅ Supported | `skills.urls` for remote skills |
| Permission controls | ✅ Supported | `permission.skill` pattern matching |
| Frontmatter fields | ✅ Supported | name, description, license, compatibility, metadata |

**Skill File Location:** `.opencode/skills/<name>/SKILL.md`

### Permissions

| Permission Key | Type | Notes |
|---------------|------|-------|
| read | Pattern | File path matching |
| edit | Pattern | write, edit, patch |
| glob | Pattern | Glob pattern matching |
| grep | Pattern | Regex pattern matching |
| bash | Pattern | Command matching |
| task | Pattern | Subagent name matching |
| skill | Pattern | Skill name matching |
| lsp | Non-granular | |
| question | Flat | ask/allow/deny only |
| webfetch | Flat | URL matching |
| websearch | Flat | Query matching |
| external_directory | Pattern | Path outside worktree |
| doom_loop | Flat | Recovery prompts |
| todowrite | Flat | Todo operations |

**Actions:** `"allow"`, `"ask"`, `"deny"`

### References

| Feature | Status | Notes |
|---------|--------|-------|
| Local paths | ✅ Supported | `path` field |
| Git repositories | ✅ Supported | `repository` field |
| Hidden references | ✅ Supported | `hidden: true` |

### Models

- Provider/model format: `anthropic/claude-sonnet-4-6`
- `small_model` for lightweight tasks
- Model override per agent

### Context Management

- `compaction` configuration for auto-context management
- `tool_output` limits for truncation
- `snapshot` for filesystem tracking

---

## 2. UNSUPPORTED Features

| Feature | Status | Reason |
|---------|--------|--------|
| Agent singular directory | ❌ Not supported | Must use `agents/` plural |
| Command singular directory | ❌ Not supported | Must use `commands/` plural |
| Agent in agents/ subdir | ❌ Not supported | Only top-level files |
| Custom agent modes beyond primary/subagent | ❌ Not supported | `mode` enum is fixed |
| Inline agent prompt without file | ⚠️ Limited | File-based recommended for complex agents |
| Pattern-based permission for question | ❌ Not supported | Flat action only |
| Pattern-based permission for webfetch/websearch | ⚠️ Limited | URL/query matching only |
| Dynamic skill loading | ❌ Not supported | Skills loaded on-demand via `skill` tool |

---

## 3. DEPRECATED Features

| Feature | Deprecated | Replacement |
|---------|------------|-------------|
| `tools` in agent config | ✅ v1.1.1 | `permission` field |
| `maxSteps` | ✅ | `steps` |
| `reference` | ✅ | `references` |
| `autoshare` | ✅ | `share` |
| `layout` | ✅ | Removed |
| `mode.build/plan` | ✅ | `agent.build/plan` |

---

## 4. RECOMMENDED Patterns

### Agent Definition (File-based)
```markdown
---
description: Agent description
mode: subagent
model: anthropic/claude-sonnet-4-6
permission:
  edit: deny
  bash: ask
---

System prompt here...
```

### Command Definition
```markdown
---
description: Command description
agent: build
---

Template prompt with $ARGUMENTS...
```

### Skill Structure
```
.opencode/skills/<name>/
  └── SKILL.md
```

### Permission Pattern (Last match wins)
```json
{
  "bash": {
    "*": "ask",
    "git *": "allow",
    "grep *": "allow",
    "rm *": "deny"
  }
}
```

---

## 5. REJECTED IDEAS (Not in OpenCode)

After documentation review, the following are **NOT supported**:

1. **Orchestrator as workflow controller** - OpenCode does not have a built-in orchestrator pattern. The `orchestrator` agent is just a named agent like any other.

2. **Parallel task dispatch** - No native parallel task feature. Use `task` tool to invoke subagents, but sequential by design.

3. **Task queue management** - Not a feature. Subagents run synchronously when invoked.

4. **Custom agent modes** - Only `primary`, `subagent`, `all` supported.

5. **Workflow engine** - No workflow orchestration built-in.

6. **Agent chaining rules** - Must manually invoke subagents via `@` or Task tool.

7. **MCP server creation** - MCP servers are external; OpenCode consumes them.

8. **Custom tools via config** - Custom tools require plugins (SDK).

---

## 6. FUTURE ROADMAP INDICATIONS

From documentation:
- Compaction improvements in progress
- Policy system (experimental)
- OpenTelemetry support (experimental)

---

## 7. CONFIGURATION ISSUES FOUND

Current `opencode.json` has problems:
1. `default_agent: "orchestrator"` but no `orchestrator` agent defined with `mode: primary`
2. `agents` section uses non-standard key (`agents` instead of `agent`)
3. References to agents in AGENTS.md that don't exist (`@architect`, `@coder`, `@documenter`, `@cloud-sync`, `@experiment-runner`)
4. No `.opencode/agents/` directory exists
5. No `.opencode/commands/` directory exists
6. No `.opencode/skills/` directory exists

---

## 8. VALIDATION

- Schema: https://opencode.ai/config.json
- Documentation: https://opencode.ai/docs
- Repository: https://github.com/anomalyco/opencode

---

*Documentation trumps assumptions. This research is based on official docs dated 2026-07-14.*