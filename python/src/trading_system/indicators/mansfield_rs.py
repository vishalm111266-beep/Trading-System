"""Mansfield Relative Strength indicator."""

from __future__ import annotations

from trading_system.indicators.moving_average import sma
from trading_system.indicators.relative_strength import relative_strength


def mansfield_rs(
    stock_prices: list[float],
    benchmark_prices: list[float],
    timestamps: list,
    lookback: int = 1,
    ma_period: int = 50,
) -> list[float | None]:
    """Compute Mansfield Relative Strength.

    Mansfield RS = (RS - SMA(RS)) / SMA(RS) * 100

    A positive value means the stock is outperforming its own
    moving-average-adjusted benchmark.
    """
    if lookback < 1:
        msg = f"lookback must be >= 1, got {lookback}"
        raise ValueError(msg)
    if ma_period < 1:
        msg = f"ma_period must be >= 1, got {ma_period}"
        raise ValueError(msg)

    signals = relative_strength(
        stock_prices, benchmark_prices, timestamps, lookback
    )
    rs_values = [s.rs_value for s in signals]
    rs_ma = sma(rs_values, ma_period)

    result: list[float | None] = [None] * (lookback)
    for i, (rs_val, rs_ma_val) in enumerate(zip(rs_values, rs_ma, strict=True)):
        if rs_ma_val is None or rs_ma_val == 0.0:
            result.append(None)
        else:
            result.append((rs_val - rs_ma_val) / rs_ma_val * 100.0)
    return result
