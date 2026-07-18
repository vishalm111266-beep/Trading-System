---
name: backtest-review
description: Review and evaluate backtest results for a strategy. Use when user says "review backtest", "backtest results", or "analyze backtest performance".
---

# Backtest Review Skill

## When to use

Use when backtest results are available and need evaluation. Typically invoked after @experiment-runner completes a backtest.

## Review Framework

### Performance Metrics to Extract

| Metric | What it tells us |
|--------|-----------------|
| Total Return | Overall strategy performance |
| Annualized Return | Normalized yearly performance |
| Sharpe Ratio | Risk-adjusted return (target: >1.0) |
| Sortino Ratio | Downside risk-adjusted return |
| Max Drawdown | Largest peak-to-trough loss |
| Win Rate | Percentage of profitable trades |
| Profit Factor | Gross profit / gross loss (>1.0 is good) |
| Avg Win/Loss | Size ratio of wins vs losses |
| Trade Count | Statistical significance |

### Verdict Criteria

```
ROBUST:    Sharpe > 1.0, Max DD < 20%, Win Rate > 45%, Trade Count > 30
NEEDS WORK: Sharpe 0.5-1.0 OR Max DD 20-35%
FLAWED:    Sharpe < 0.5 OR Max DD > 35% OR Trade Count < 20
```

### Common Pitfalls to Check

1. **Overfitting** — Too few trades relative to parameters
2. **Look-ahead bias** — Entry signal uses data not available at that time
3. **Survivorship bias** — Only testing stocks that survived to present
4. **Transaction costs** — Are commissions, slippage, and spread included?
5. **Regime sensitivity** — Does it work in both bull and bear markets?

## Output Format

```
BACKTEST REVIEW:
- Verdict: [ROBUST / NEEDS WORK / FLAWED]
- Confidence: [HIGH / MEDIUM / LOW]

Key Metrics:
| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Sharpe | X.XX | >1.0 | PASS/FAIL |
| Max DD | X% | <20% | PASS/FAIL |
| Win Rate | X% | >45% | PASS/FAIL |
| Trades | N | >30 | PASS/FAIL |

Pitfalls Detected:
- [list or "None identified"]

Recommendation:
- [PROCEED / REFINE / ABANDON]
```

## Rules

1. Report all metrics, even if verdict is FLAWED
2. Never modify backtest code — only review and report
3. Flag if transaction costs are missing from calculation
4. If robustness is unclear, invoke @reviewer for second opinion
5. Do not recommend live trading based solely on backtest results