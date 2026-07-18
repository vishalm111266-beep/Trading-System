# Indian Market Reference Data

This directory contains market-specific reference data for Indian markets (NSE/BSE).

## Contents

| File | Description |
|------|-------------|
| `holidays.yaml` | NSE/BSE holiday calendar |
| `circuit_limits.yaml` | Per-stock circuit breaker limits |
| `tax_rules.yaml` | STT, GST, stamp duty reference |
| `trading_hours.yaml` | Market open/close times |

## Rules

- Reference data only — no execution logic
- All data must be sourced from official exchanges
- Update annually at year start
- Do not mix with US market data