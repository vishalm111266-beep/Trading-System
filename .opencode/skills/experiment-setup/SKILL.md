---
name: experiment-setup
description: Set up a new isolated research experiment folder. Use when user says "new experiment", "start research", "run analysis", or "create experiment".
---

# Experiment Setup Skill

## When to use

Use when user wants to run any analysis, backtest, or research session. Every research activity goes through this skill.

## Pipeline

1. **Validate** — Is this a new experiment or a continuation? Check existing `research/` folders
2. **Name** — Assign `exp-XXX-name` following next available sequence number
3. **Create folder structure**:
   ```
   research/exp-XXX-name/
   ├── notes.md       # experiment parameters
   ├── config/        # configuration files
   └── outputs/       # generated artifacts (plots, reports, CSVs)
   ```
4. **Create notes.md** — Document ticker, date range, approach, hypothesis
5. **Invoke @experiment-runner** to execute the experiment

## Naming Convention

- Format: `exp-NNN-name` where NNN is a 3-digit sequential number
- name: short, lowercase, hyphenated (e.g., `reliance-rs`, `nifty-sma-backtest`)
- Find next number by checking existing folders in `research/`

## Notes Template

```markdown
# Experiment: [name]
- Created: [YYYY-MM-DD]
- Ticker: [normalized]
- Market: [INDIAN/US]
- Date range: [start] to [end]
- Approach: [what we are testing]
- Hypothesis: [what we expect to find]
- Status: OPEN
```

## Rules

1. One experiment per folder — never nest
2. Never modify notes.md after experiment is closed
3. All outputs go to `outputs/` — never to parent directories
4. Close experiment (set status: CLOSED) after review
5. After closing, await user decision: discard or promote to strategies/

## Cleanup After Setup

If experiment setup fails mid-way, remove the partially created folder before retrying.