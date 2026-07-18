# Agent Invocation Patterns — User Guide

> This document outlines how to invoke agents for common workflows. The user is the orchestrator.

## Guiding Principles

1. **User is the Orchestrator:** You decide which agent to use and when. There is no automatic routing.
2. **Use Native Agents First:** Prefer built-in agents (`@build`, `@general`, `@plan`, `@explore`) over custom ones.
3. **Use Skills for Knowledge:** Domain-specific logic (e.g., how to do technical analysis) lives in skills, which agents can load on-demand.
4. **Use Commands for Shortcuts:** Commands (`/analyze`, `/backtest`) are convenient shortcuts for complex prompts that invoke native agents and skills.

## Workflow Invocation Patterns

| Task | Recommended Command | Native Agent | Key Skills Involved |
|------|----------------------|--------------|---------------------|
| Code Change | `(@build)` | `@build` | `(none)` |
| Research Task | `(@general)` | `@general` | `research-methodology` |
| Multi-step Analysis | `/analyze <TICKER>` | `@general` | `technical-analysis`, `sentiment-analysis`, `risk-management` |
| Backtesting | `/backtest <STRATEGY>` | `@build` | `backtest-strategy`, `experiment-setup` |
| Strategy Dev | `/strategy <NAME>` | `@build` | `strategy-development`, `research-methodology` |
| Portfolio Analysis | `/portfolio` | `@general` | `portfolio-optimization`, `risk-management` |
| Market Scan | `/scan <CRITERIA>` | `@general` | `(specific scan skills)` |
| Code Review | `/review` | `@plan` / `@explore`| `code-review` |

## Workflow Rules

1. **Research Workflow:** User invokes `@general` with a research prompt. The agent may load the `research-methodology` skill.
2. **Code Change Workflow:** User invokes `@build` to implement, test, and review code.
3. **No agent may approve its own output.** User is responsible for verification.

## Market Detection

- Indian: `.NS`, `.BO`, NSE, BSE, NIFTY, BANKNIFTY, or Indian stock names.
- US: `.US`, NYSE, NASDAQ, S&P, or US stock names.
- Default Indian suffix: `.NS`

Market detection is handled by commands and skills, not by a central routing agent.
