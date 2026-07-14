# Trading System

Phone-first institutional trading research workspace built on Android + Termux + Ubuntu Proot.

## Overview

A modular environment for developing, testing, and analyzing trading strategies across Python and TradingView Pine Script. Designed to run entirely on a mobile device with a desktop-class Linux environment.

## Architecture

```
Trading-System/
├── config/          # Models, templates, workflow configs
├── data/            # Market data, datasets
├── docs/            # Architecture, guides, reference
├── pine/            # Pine Script indicators, libraries, strategies
├── python/          # Python backtests, indicators, strategies, utilities
├── reports/         # Generated analysis reports
├── research/        # Active research, findings, sources
├── scripts/         # Setup, backup, update, utility scripts
└── tests/           # Unit, integration, backtest tests
```

## Target Environment

- **OS:** Android with Termux + Ubuntu Proot
- **Languages:** Python 3, Pine Script v5
- **Data:** Local-first, API-sourced market data

## Quick Start

```bash
# From Termux
pkg install proot-distro
proot-distro install ubuntu
proot-distro login ubuntu

# Inside Ubuntu Proot
apt update && apt upgrade -y
apt install python3 python3-pip git
git clone <repo-url> ~/Trading-System
cd ~/Trading-System
scripts/setup/bootstrap.sh
```

## Documentation

- [FOUNDATION.md](FOUNDATION.md) - System principles and constraints
- [WORKFLOW.md](WORKFLOW.md) - Development and research workflow
- [ROADMAP.md](ROADMAP.md) - Project phases and milestones
- [DECISIONS.md](DECISIONS.md) - Architectural decision records
- [AGENTS.md](AGENTS.md) - AI agent operating instructions
- [CHANGELOG.md](CHANGELOG.md) - Release history

## License

See [LICENSE](LICENSE).
