"""Relative strength signal model."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class RSSignal:
    """A single relative-strength data point."""

    timestamp: datetime
    stock_return: float
    benchmark_return: float
    rs_value: float

    def __post_init__(self) -> None:
        if self.benchmark_return == 0.0:
            msg = "benchmark_return must not be zero"
            raise ValueError(msg)
        if self.rs_value <= 0.0:
            msg = f"rs_value must be positive, got {self.rs_value}"
            raise ValueError(msg)
