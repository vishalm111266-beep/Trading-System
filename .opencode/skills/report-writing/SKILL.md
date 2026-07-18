---
name: report-writing
description: Write structured research reports from experiment outputs. Use when user says "write report", "document findings", or "summarize results".
---

# Report Writing Skill

## When to use

Use when experiment results need to be documented for future reference or sharing.

## Report Location

Reports are saved to the experiment's `outputs/` folder:
```
research/exp-XXX-name/outputs/report.md
```

## Report Structure

```markdown
# Research Report: [Experiment Name]

## Metadata
- Experiment: [exp-XXX-name]
- Date: [YYYY-MM-DD]
- Ticker: [normalized]
- Market: [INDIAN/US]

## Objective
[What we set out to investigate]

## Methodology
[How we approached it]

## Results
[What we found — use tables for metrics]

## Analysis
[Interpretation of results]

## Limitations
[Any caveats, data quality issues, known biases]

## Conclusion
[Summary with confidence level]
```

## Rules

1. Write reports in the experiment's `outputs/` folder — never in `docs/`
2. Include all relevant metrics in table format
3. State confidence level explicitly (HIGH / MEDIUM / LOW)
4. Do not include recommendations to buy/sell — only findings
5. If writing to a non-experiment context (e.g., docs/), invoke @documenter instead
6. Use market suffix conventions correctly (Indian: `.NS`, US: standard)

## Graphics

If the experiment produced charts or plots, reference them in the report:
```
![Chart description](../outputs/chart.png)
```

Do not embed large binary files in markdown — reference by path.