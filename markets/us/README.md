# US Market Reference Data

This directory contains market-specific reference data for US markets (NYSE/NASDAQ).

## Contents

| File | Description |
|------|-------------|
| `trading_hours.yaml` | NYSE/NASDAQ open/close times |
| `pdt_rules.yaml` | Pattern Day Trader rule thresholds |
| `sec_fees.yaml` | SEC fee schedule |
| `regulation.yaml` | Regulation SHO, T+1 settlement rules |

## Rules

- Reference data only — no execution logic
- All data must be sourced from official exchanges
- Update annually at year start
- Do not mix with Indian market data