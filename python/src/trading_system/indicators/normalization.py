"""Normalization utilities for numeric series."""

from __future__ import annotations

import math


def zscore(values: list[float]) -> list[float | None]:
    """Compute Z-scores for a list of values.

    Returns a list the same length as *values*. ``None`` for entries
    where the standard deviation is zero.
    """
    n = len(values)
    if n < 2:
        return [None] * n

    mean = sum(values) / n
    variance = sum((v - mean) ** 2 for v in values) / n
    std = math.sqrt(variance)

    if std == 0.0:
        return [None] * n
    return [(v - mean) / std for v in values]


def min_max(values: list[float]) -> list[float]:
    """Normalize values to the ``[0, 1]`` range.

    If all values are identical, returns a list of zeros.
    """
    if not values:
        return []
    lo = min(values)
    hi = max(values)
    span = hi - lo
    if span == 0.0:
        return [0.0] * len(values)
    return [(v - lo) / span for v in values]


def percentile(values: list[float]) -> list[float]:
    """Map each value to its percentile rank in ``[0, 100]``.

    Uses the percentage of values less than or equal to each entry.
    """
    n = len(values)
    if n == 0:
        return []
    result: list[float] = []
    for v in values:
        count = sum(1 for other in values if other <= v)
        result.append(count / n * 100.0)
    return result
