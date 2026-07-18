---
description: Parallel task orchestration — split work into independent branches and assign to subagents
agent: orchestrator
---

Invoke @orchestrator to handle parallel task orchestration:

1. **Summarize** the request in one sentence
2. **Determine** if task can be safely split into independent branches
3. **Label** each subtask by type: research, implement, review, test
4. **Assign** each branch to the best subagent (@researcher, @implementer, @reviewer, @tester)
5. **Start** with highest-value branch first
6. **Stop and ask** if task cannot be safely split

## When to Use

Use this command when you have a broad prompt that could benefit from parallel execution:
- "Build feature X" → split into research + implement + test + review
- "Analyze stock Y" → split into technical + fundamental + sentiment + risk
- "Fix bugs" → split into diagnose + fix + verify

## When NOT to Use

Do NOT use this command for:
- Simple one-line questions
- Tasks that depend on each other (must be sequential)
- Tasks that one agent can do faster alone

## Output Format

The orchestrator will return:
```
ORIGINAL REQUEST: [summary]
SPLIT PLAN: [how divided and why]
BRANCHES: [list of branches with assigned agents]
DEPENDENCY ORDER: [if any dependencies]
MERGE RULE: [how to combine results]
STOP POINT: [when to stop splitting]
```

## Command Usage

```
/parallel [your request here]
```

Or simply let the orchestrator (default agent) decide whether to split based on the prompt.