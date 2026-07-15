---
description: Full multi-agent stock analysis
agent: general
---

Run a full analysis pipeline for $ARGUMENTS:

1. @technical-analyst — analyze price action, indicators, chart patterns
2. @fundamental-analyst — evaluate financials, valuation, business quality
3. @sentiment-analyst — assess news sentiment and social media mood
4. @risk-manager — evaluate risk parameters and position sizing

Synthesize all findings into a single report with BUY/HOLD/SELL recommendation, entry/exit levels, stop loss, and confidence level.

Market detection:
- Indian stocks: append .NS if not present (RELIANCE → RELIANCE.NS)
- US stocks: use standard tickers (AAPL, TESLA)
