---
name: backtest-strategy
description: Run backtests on trading strategies. Use when user says "backtest [STRATEGY]", "run backtest", or "test strategy".
---

# Backtest Strategy Skill

## Pipeline
1. @strategy-developer → define strategy rules
2. @backtest-engineer → run backtest
3. @risk-manager → evaluate risk metrics

## Output
Backtest results with Sharpe ratio, max drawdown, win rate, profit factor.
