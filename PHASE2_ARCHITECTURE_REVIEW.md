# PHASE 2 ARCHITECTURE REVIEW

**Date:** 2026-07-15
**Status:** Awaiting Approval
**Source:** Based on https://opencode.ai/docs (verified 2026-07-14)

---

## 1. WHAT OPENCODE ACTUALLY IS

OpenCode is:
- A **coding assistant** with terminal interface
- Built around **primary agents** (build, plan) and **subagents** (general, explore, scout)
- A config-driven workspace with **commands**, **skills**, **references**, and **permissions**
- NOT a workflow engine, task queue, or orchestration system

**Critical insight:** There is NO orchestrator engine in OpenCode. Any "orchestrator" is just a named agent. The USER is the real orchestrator by choosing which agent/command to invoke.

---

## 2. ANALYSIS: THE INITIAL PROPOSAL'S FLAWS

### The Problem with "orchestrator" as workflow controller
```
User → @orchestrator → @researcher → @implementer → @reviewer → @tester
```

This architecture implies:
1. Orchestrator automatically routes tasks
2. Tasks run in parallel
3. Results automatically merge
4. A master agent coordinates everything

**Reality check:**
- OpenCode agents are invoked via `@mentions` or `task` tool
- The model decides WHEN to invoke subagents (unreliable for orchestration)
- Commands are just saved prompts (no logic engine)
- No native parallel execution
- No task queue management

**Verdict:** The initial proposal describes a system that doesn't exist in OpenCode.

### The Problem with 4 Custom Subagents (researcher, implementer, reviewer, tester)

| Agent | Built-in Alternative | Overhead |
|-------|---------------------|----------|
| researcher | @general, @explore, @plan | Extra context switch, tokens |
| implementer | @build | Redundant with build |
| reviewer | @plan (read-only) | Could use @plan with prompt |
| tester | @build with pytest | Redundant with build |

**Each custom agent adds:**
- Context switch overhead (~200-500 tokens per invocation)
- File I/O for agent definition
- Maintenance burden
- Permission configuration

### The Problem with 6 Commands (research, plan, implement, review, test, parallel)

- `/parallel` implies parallelism OpenCode doesn't have
- Commands are just templates - they don't add automation
- Each command is a file to maintain
- Most can be replaced with direct @agent invocations

---

## 3. PRINCIPLES FOR THE REDESIGN

### Principle 1: Embrace OpenCode's Design
OpenCode is a coding assistant. WORK WITH IT, not against it.

### Principle 2: User is the Orchestrator
The user decides what to do. OpenCode agents execute. This is the only reliable architecture.

### Principle 3: Minimize Custom Code
Every custom agent/command/skill is code to maintain. Use built-ins when possible.

### Principle 4: Optimize for Constraints
- Android phone: Low memory
- Minimal context: Use compaction, prune, snapshot=false
- Long conversations: Skill loading on-demand
- Large repos: Use @explore for read-only operations

### Principle 5: Permissions as Architecture
Use permissions to enforce boundaries, not custom agents.

---

## 4. PROPOSED ARCHITECTURE

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER (ORCHESTRATOR)                      │
│                  Decides WHAT to do, WHEN to do it              │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    OPENCODE WORKSPACE                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐   │
│  │    PLAN      │     │    BUILD     │     │   EXPLORE    │   │
│  │  (thinking)  │◄───►│ (implement) │◄───►│  (discover)  │   │
│  │  edit: ask   │     │  edit: allow │     │  edit: deny  │   │
│  │  bash: ask   │     │  bash: allow │     │  bash: deny  │   │
│  └──────────────┘     └──────────────┘     └──────────────┘   │
│         │                    │                    │            │
│         │                    │                    │            │
│         ▼                    ▼                    ▼            │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐   │
│  │   GENERAL    │     │   REVIEWER   │     │   TESTER     │   │
│  │  (multistep) │     │   (custom)   │     │   (custom)   │   │
│  │  edit: allow │     │  edit: deny  │     │ bash: scoped │   │
│  │  bash: allow │     │  bash: deny  │     │              │   │
│  └──────────────┘     └──────────────┘     └──────────────┘   │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│  COMMANDS (shortcuts to invoke subagents with templates)        │
│  /review  /test                                                 │
│                                                                  │
│  SKILLS (on-demand reusable prompts)                            │
│  task-decomposition  research-methodology  code-review         │
│                                                                  │
│  REFERENCES (external context)                                  │
│  @docs  @markets                                                │
└─────────────────────────────────────────────────────────────────┘
```

### Agent Hierarchy

| Agent | Type | Purpose | Why It Exists |
|-------|------|---------|---------------|
| plan | built-in primary | Thinking, analysis, planning | Naturally restricts edits/bash to "ask" |
| build | built-in primary | Implementation | Full access, default for coding |
| explore | built-in subagent | Code discovery | Fast, read-only, for large repos |
| general | built-in subagent | Complex multistep tasks | Can run multiple units of work |
| **reviewer** | custom subagent | Code review | Only agent that should have read-only + description focus |
| **tester** | custom subagent | Test execution | Only agent with scoped bash (pytest/ruff only) |

**Why only 2 custom agents?**

1. **reviewer**: Every other review-capable agent (plan, explore) is optimized for OTHER purposes. Plan is for planning, explore is for discovery. Reviewer is the ONLY agent whose SOLE purpose is review with a specific methodology.

2. **tester**: The ONLY agent that needs BASH but not full bash. All other agents with bash (build, general) have unrestricted bash. Tester is the ONLY way to restrict bash to specific commands (pytest, ruff).

**Could other agents do the same job?**

- @plan could do reviews, but its prompt is for planning, not systematic review
- @explore could do reviews, but it's optimized for file discovery, not review methodology
- @build could run tests, but it also has full edit access (too permissive for test-only tasks)

**Could they be merged?**
No. Permissions are the key distinction. Reviewer must have edit:deny, bash:deny. Tester must have bash scoped to pytest/ruff. These are fundamentally different permission sets.

### Command Hierarchy

| Command | Target | Purpose | Why Command |
|---------|--------|---------|------------|
| /review | @reviewer | Initiate code review | Consistent review template, subtask mode |
| /test | @tester | Run tests | Consistent test invocation, scoped bash |

**Why not /research, /implement, /plan?**

- `/research`: User can just type "@general help me research..." - same tokens, less maintenance
- `/implement`: User can just type "@build help me implement..." - same tokens, less maintenance
- `/plan`: User can just switch to plan mode with Tab - built-in behavior

**Commands are for:** When you want the SAME template every time, invoked the SAME way, with consistent subtask behavior.

**NOT for:** When direct @agent invocation works just as well.

### Skill Hierarchy

| Skill | Purpose | When Used | Why Skill |
|-------|---------|-----------|-----------|
| task-decomposition | How to break down work | Planning complex tasks | Reusable thinking pattern, loaded on-demand |
| research-methodology | How to research | Doing research tasks | Reusable research pattern, loaded on-demand |
| code-review | How to review code | Doing reviews | Methodology guide, loaded on-demand |

**Why these 3 skills?**

1. **task-decomposition**: Thinking methodology that should be consistent across ALL planning tasks. NOT a command because it's a PATTERN, not a template.

2. **research-methodology**: How to research is complex enough to warrant a reusable skill. Includes source evaluation, fact-checking, citation.

3. **code-review**: Review methodology should be consistent. Reviewer agent has the PERMISSIONS, but the skill has the METHODOLOGY.

**Why NOT more skills?**

- python-best-practices: This is a REFERENCE doc, not a skill. Put it in docs/.
- documentation: This is EXECUTION, not methodology. Use @build.
- github-workflow: This is TOOL USAGE, not methodology. Use commands when needed.

### Permission Model

```
Global Permissions (opencode.json):
├── read: allow
├── edit: ask (user must approve edits)
├── glob: allow
├── grep: allow
├── list: allow
├── bash:
│   ├── "pytest *": allow
│   ├── "ruff *": allow
│   ├── "git *": allow
│   └── "*": ask
├── task: allow
├── skill: allow
├── lsp: allow
├── question: allow
├── webfetch: allow
├── websearch: allow
├── external_directory: ask
└── doom_loop: ask

Agent Permissions:
├── plan: uses global (edit:ask, bash:ask forces user approval)
├── build: uses global (edit:allow, bash:allow for implementation)
├── explore: edit:deny, bash:deny (read-only discovery)
├── general: uses global (full access for complex tasks)
├── reviewer: edit:deny, bash:deny, read:allow (pure review)
└── tester: edit:deny, bash:scoped (pytest/ruff only)
```

**Key insight:** Permissions define what CAN happen. User approval defines what DOES happen.

### Context Management Strategy

```
1. Snapshot: disabled (save memory on large repos)

2. Compaction:
   ├── auto: true (compact when context full)
   ├── prune: true (remove old tool outputs)
   └── reserved: 8000 (keep 8k tokens for compaction safety)

3. Tool Output:
   ├── max_lines: 500 (truncate verbose output)
   └── max_bytes: 16384 (16KB per tool output)

4. Skills: loaded on-demand only (never preload)
```

**Why this matters:**
- Snapshot=false saves git indexing overhead
- Prune=true removes old outputs from context
- Small tool_output limits prevent token blowup
- On-demand skills keep context clean

### Token Optimization Strategy

1. **Use @explore for large repo operations** - It's read-only and optimized for discovery
2. **Use /review command with subtask** - Review happens in subagent context, not main context
3. **Use skills on-demand** - Don't load methodology until needed
4. **Use references for docs** - @docs instead of loading docs into context
5. **Switch to plan for thinking** - plan mode naturally restricts, making the model more concise

### Memory Optimization Strategy

1. **Disable snapshot** - No git indexing overhead
2. **Prune old tool outputs** - Compact removes them from context
3. **Small model for simple tasks** - Use small_model for title generation, keep main model for complex work
4. **Subtask mode for reviews** - Review context doesn't pollute main context

---

## 5. COMPARISON: INITIAL PROPOSAL VS REDESIGN

| Aspect | Initial Proposal | Redesign |
|--------|------------------|----------|
| Custom Agents | 5 (orchestrator, researcher, implementer, reviewer, tester) | 2 (reviewer, tester) |
| Custom Commands | 6 (research, plan, implement, review, test, parallel) | 2 (review, test) |
| Skills | 7 (task-decomposition, research-methodology, code-review, etc.) | 3 (task-decomposition, research-methodology, code-review) |
| Orchestrator | Fake engine (doesn't exist) | User is the orchestrator |
| Parallel Execution | Claimed but fake | No parallelism (doesn't exist) |
| Task Queue | Claimed but fake | No queue (doesn't exist) |
| Memory Usage | High (5 agents + 6 commands + 7 skills) | Low (2 agents + 2 commands + 3 skills) |
| Files to Maintain | 18+ | 7 |
| Leverages Built-ins | No | Yes |

---

## 6. RISKS

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| User expects orchestration that doesn't exist | High | Clear docs that user is orchestrator |
| Reviewer agent is redundant | Medium | Use if review methodology is distinct enough |
| Tester agent is redundant | Low | Only way to scope bash to pytest/ruff |
| Skills add overhead without benefit | Medium | Start with just task-decomposition |
| Config complexity | Low | Simple, well-documented |

---

## 7. TRADE-OFFS

| Trade-off | Chosen Side | Rationale |
|-----------|-------------|-----------|
| Custom agents vs built-ins | Minimal custom | Reduce maintenance, leverage OpenCode |
| Many commands vs few | Few | Direct @invocation works just as well |
| Many skills vs few | Few | Only methodology patterns warrant skills |
| Fake orchestration vs user orchestration | User orchestration | Only reliable architecture |

---

## 8. WHY THIS DESIGN IS BETTER

1. **It's REAL**: This architecture actually works with OpenCode. The initial proposal describes a system that doesn't exist.

2. **It's SIMPLE**: 7 files to maintain vs 18+. Less is more.

3. **It's OPTIMIZED**: Built for Android/low-RAM with compaction, prune, snapshot=false.

4. **It WORKS WITH OpenCode**: Uses built-in agents, commands, skills as designed.

5. **User is in control**: Clear model where user orchestrates, agents execute.

6. **Permissions enforce boundaries**: No agent can do more than it should.

7. **Future compatible**: Uses only documented features, no hacks.

---

## 9. FILES TO CREATE (Phase 2 Implementation)

```
.opencode/
├── agents/
│   └── reviewer.md       # Code review agent (edit:deny, bash:deny)
├── commands/
│   ├── review.md         # /review command invoking @reviewer
│   └── test.md           # /test command invoking @tester
├── skills/
│   └── task-decomposition/
│       └── SKILL.md      # How to break down work
```

**Wait - where are the other files?**

- **researcher, implementer**: Use @general, @build directly
- **tester agent**: NOT NEEDED - use @build with pytest permission (or create if bash scoping is critical)
- **research-methodology skill**: Could add later if research becomes complex
- **code-review skill**: Could add later if reviewer needs methodology guide

**Minimum viable implementation:** Just `reviewer.md` and `review.md` command. Everything else can use built-ins.

---

## 10. PHASE 2 IMPLEMENTATION PLAN (If Approved)

### Minimal (2 files):
1. `.opencode/agents/reviewer.md` - Read-only review agent
2. `.opencode/commands/review.md` - /review command

### Recommended (4 files):
1. `.opencode/agents/reviewer.md`
2. `.opencode/commands/review.md`
3. `.opencode/commands/test.md`
4. `.opencode/skills/task-decomposition/SKILL.md`

### Optional (if needed):
- `.opencode/agents/tester.md` - If bash scoping is critical
- `.opencode/skills/research-methodology/SKILL.md`
- `.opencode/skills/code-review/SKILL.md`

---

## 11. QUESTIONS FOR APPROVAL

1. **Is the minimal approach acceptable?** (reviewer agent + /review command only)

2. **Is the recommended approach acceptable?** (reviewer, tester, commands, task-decomposition skill)

3. **Do you want the full optional implementation?**

4. **Should I keep the existing AGENTS.md or replace it entirely?**

5. **Should I fix the opencode.json config bugs first?**

---

*Architecture review complete. Awaiting approval before implementation.*