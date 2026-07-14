# ROADMAP.md

Project phases and milestones.

## Phase 0: Foundation (Current)

**Goal:** Establish working environment and core infrastructure.

### Milestones
- [x] Repository structure created
- [x] Documentation framework established
- [ ] Termux + Proot bootstrap script
- [ ] Python environment setup and dependency management
- [ ] Basic data fetching and storage pipeline
- [ ] Test infrastructure operational

### Deliverables
- `scripts/setup/bootstrap.sh` - One-command environment setup
- `python/src/` - Core library initialization
- `tests/` - Test runner and CI configuration

---

## Phase 1: Data Infrastructure

**Goal:** Reliable local data storage and retrieval.

### Milestones
- [ ] Market data API clients (OHLCV, fundamentals)
- [ ] Local SQLite or Parquet storage layer
- [ ] Data validation and integrity checks
- [ ] Historical data backfill capability
- [ ] Data retention and cleanup policies

### Deliverables
- `python/data/` - Data access layer
- `data/` - Organized storage with metadata
- `scripts/setup/` - Data management scripts

---

## Phase 2: Analysis Tools

**Goal:** Core analysis and backtesting capabilities.

### Milestones
- [ ] Indicator calculation engine
- [ ] Backtesting framework
- [ ] Performance metrics computation
- [ ] Report generation
- [ ] Pine Script indicator library

### Deliverables
- `python/indicators/` - Indicator library
- `python/backtests/` - Backtesting engine
- `reports/` - Automated report generation
- `pine/indicators/` - TradingView indicators

---

## Phase 3: Research Workflow

**Goal:** Structured research process with traceability.

### Milestones
- [ ] Research template system
- [ ] Finding documentation format
- [ ] Source tracking and citation
- [ ] Research archive and search
- [ ] Cross-referencing between research and code

### Deliverables
- `research/templates/` - Standardized research formats
- `research/active/` - Current research workspace
- `research/archive/` - Completed research

---

## Phase 4: Automation

**Goal:** Streamlined daily operations.

### Milestones
- [ ] Scheduled data updates
- [ ] Automated report generation
- [ ] Backup and sync scripts
- [ ] Health monitoring and alerts
- [ ] Workflow automation

### Deliverables
- `scripts/update/` - Data and code update scripts
- `scripts/backup/` - Backup and restore tools
- `scripts/utils/` - Utility automation

---

## Success Criteria

The system is production-ready when:

1. Environment setup takes < 10 minutes from fresh Proot install
2. Data pipeline runs unattended on schedule
3. Backtests complete in < 5 minutes for standard datasets
4. All tests pass consistently
5. Reports generate automatically with no manual intervention
