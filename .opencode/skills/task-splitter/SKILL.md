---
name: task-splitter
description: Analyzes complex tasks and splits them into independent parallel branches and dependent sequential chains. Use when user says "split task", "parallelize", "analyze dependencies", or "break down work".
---

# Task Splitter Skill

Analyzes complex tasks and determines optimal execution strategy.

## When to Use

Use this when:
- Task is complex and could benefit from parallel execution
- Unclear what can run independently vs. what has dependencies
- Need to plan multi-agent orchestration

## How to Analyze

### Step 1: List All Subtasks

Break the request into atomic, independent units.

### Step 2: Identify Dependencies

For each subtask, determine:
- Does it need output from another subtask?
- Does it work on the same files as another subtask?
- Does it require context from another subtask?

### Step 3: Categorize

| Category | Symbol | Description |
|----------|--------|-------------|
| Independent | `[I]` | Can run in parallel with anything |
| Dependent | `[D]` | Must wait for another subtask |
| Blocking | `[B]` | No other work can start until this completes |

### Step 4: Build Execution Plan

```
PARALLEL GROUP 1:
  - [I] Subtask A
  - [I] Subtask B
  - [I] Subtask C

↓
SEQUENTIAL (depends on GROUP 1):
  - [D] Subtask D (needs Subtask A output)
  - [D] Subtask E (needs Subtask B output)

↓
PARALLEL GROUP 2:
  - [I] Subtask F
  - [I] Subtask G
```

## Output Format

Provide:
1. **Subtask List**: All atomic tasks identified
2. **Dependency Graph**: Which tasks depend on which
3. **Execution Plan**: Ordered list of what to run when
4. **Agent Assignment**: Which agent最适合 each subtask

## Rules

1. **Max 5 parallel tasks per group** — more creates merge complexity
2. **Max 3 agents in a chain** — longer chains have compounding errors
3. **Independent tasks MUST be parallel** — never sequential if independent
4. **Self-contained prompts** — each subagent needs all context in its prompt