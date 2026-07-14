"""Moving average calculations."""

from __future__ import annotations


def sma(values: list[float], period: int) -> list[float | None]:
    """Simple Moving Average.

    Returns a list the same length as *values*. The first ``period - 1``
    entries are ``None`` (insufficient data).
    """
    if period < 1:
        msg = f"period must be >= 1, got {period}"
        raise ValueError(msg)
    result: list[float | None] = []
    window_sum = 0.0
    for i, v in enumerate(values):
        window_sum += v
        if i >= period:
            window_sum -= values[i - period]
        if i >= period - 1:
            result.append(window_sum / period)
        else:
            result.append(None)
    return result


def ema(values: list[float], period: int) -> list[float | None]:
    """Exponential Moving Average.

    Uses SMA of the first ``period`` values as the seed.
    Returns a list the same length as *values*. The first ``period - 1``
    entries are ``None``.
    """
    if period < 1:
        msg = f"period must be >= 1, got {period}"
        raise ValueError(msg)
    if len(values) < period:
        return [None] * len(values)

    multiplier = 2.0 / (period + 1)
    result: list[float | None] = [None] * (period - 1)

    seed = sum(values[:period]) / period
    result.append(seed)

    prev = seed
    for v in values[period:]:
        current = (v - prev) * multiplier + prev
        result.append(current)
        prev = current
    return result
