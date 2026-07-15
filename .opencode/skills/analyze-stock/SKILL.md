---
name: analyze-stock
description: Full multi-agent stock analysis combining technical, fundamental, sentiment, and risk. Use when user says "analyze [STOCK]", "analysis of [STOCK]", or "what do you think about [STOCK]".
---

# Analyze Stock Skill

## Pipeline
1. @technical-analyst → price action, indicators, signals
2. @fundamental-analyst → financials, valuation
3. @sentiment-analyst → news, mood
4. @risk-manager → risk assessment

## Output
Combined analysis with BUY/HOLD/SELL recommendation, entry/exit levels, risk parameters.

## Market Detection
- Indian stocks: .NS suffix (RELIANCE.NS, TCS.NS)
- US stocks: standard tickers (AAPL, TESLA)
