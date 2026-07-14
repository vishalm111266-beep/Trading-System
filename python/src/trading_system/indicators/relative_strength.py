"""Relative Strength calculation against a benchmark."""

from __future__ import annotations

from datetime import datetime

from trading_system.models.rs_signal import RSSignal


def _period_return(prices: list[float], index: int, lookback: int) -> float:
    """Percentage return from ``index - lookback`` to ``index``."""
    base = prices[index - lookback]
    if base == 0.0:
        msg = "base price is zero"
        raise ValueError(msg)
    return (prices[index] - base) / base


def relative_strength(
    stock_prices: list[float],
    benchmark_prices: list[float],
    timestamps: list[datetime],
    lookback: int = 1,
) -> list[RSSignal]:
    """Compute RS signals for aligned price series.

    *stock_prices* and *benchmark_prices* must have the same length and
    correspond 1-to-1 with *timestamps*.

    Each signal's ``rs_value`` is ``stock_return / benchmark_return``.
    """
    n = len(stock_prices)
    if n != len(benchmark_prices):
        msg = f"length mismatch: stock={n}, benchmark={len(benchmark_prices)}"
        raise ValueError(msg)
    if n != len(timestamps):
        msg = f"length mismatch: prices={n}, timestamps={len(timestamps)}"
        raise ValueError(msg)
    if lookback < 1:
        msg = f"lookback must be >= 1, got {lookback}"
        raise ValueError(msg)
    if n <= lookback:
        msg = f"need at least {lookback + 1} data points, got {n}"
        raise ValueError(msg)

    signals: list[RSSignal] = []
    for i in range(lookback, n):
        stock_ret = _period_return(stock_prices, i, lookback)
        bench_ret = _period_return(benchmark_prices, i, lookback)
        if bench_ret == 0.0:
            msg = f"benchmark return is zero at index {i}"
            raise ValueError(msg)
        rs_val = stock_ret / bench_ret
        signals.append(
            RSSignal(
                timestamp=timestamps[i],
                stock_return=stock_ret,
                benchmark_return=bench_ret,
                rs_value=rs_val,
            )
        )
    return signals
