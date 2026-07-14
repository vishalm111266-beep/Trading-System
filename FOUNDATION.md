# FOUNDATION.md

Core principles, constraints, and system invariants for the Trading System.

## Principles

### Phone-First
The primary interface is a phone running Termux with Ubuntu Proot. Every tool, script, and workflow must function without a desktop environment, GUI, or mouse dependency.

### Local-First
Data, code, and results live on the device. External APIs are fetched and stored locally. No dependency on cloud services for core functionality.

### Modular
Each directory is a self-contained module with a single responsibility. Modules communicate through well-defined interfaces, not shared state.

### Production-Ready
Every component must handle edge cases, validate inputs, and fail gracefully. There is no "prototype" mode.

## Constraints

| Constraint | Detail |
|---|---|
| No GPU | All computation is CPU-bound. Optimize for throughput over latency. |
| No Docker | Proot is the isolation layer. Scripts must run natively in Proot Ubuntu. |
| No GUI | All output is text-based. Use tables, structured logs, plain text reports. |
| Limited RAM | Typical Termux session: 2-4 GB. Avoid unbounded caches or large allocations. |
| Limited Storage | Phone storage is finite. Implement data retention policies. |

## Module Responsibilities

| Module | Purpose |
|---|---|
| `config/` | Runtime configuration, model definitions, workflow templates |
| `data/` | Raw and processed market data, local caching |
| `pine/` | TradingView Pine Script indicators and strategies |
| `python/` | Backtesting engine, data pipelines, analysis tools |
| `reports/` | Generated output: backtest results, analysis summaries |
| `research/` | Research notes, findings, source materials |
| `scripts/` | Setup, maintenance, automation scripts |
| `tests/` | Verification suite across all modules |

## Data Flow

```
Market APIs → data/ → python/ (processing) → reports/
                         ↑
                    research/ (findings)
                         ↑
                    config/ (parameters)
```

## Technology Stack

- **Python 3.10+** - Core computation and backtesting
- **Pine Script v5** - TradingView indicators and strategies
- **Shell (bash/sh)** - Automation and setup scripts
- **Git** - Version control and change tracking

## Non-Goals

- Real-time order execution
- Portfolio management
- Trading signal generation
- Risk management automation
- Any automated trading activity

This system is a **research workspace**. All trading decisions are made manually by the operator.
