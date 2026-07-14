"""Strategy evaluation orchestration."""

from __future__ import annotations

from trading_system.scanner.result import ScanResult
from trading_system.strategies.base import Strategy
from trading_system.strategies.signal import Signal


class StrategyEvaluator:
    """Applies a :class:`Strategy` to a :class:`ScanResult`."""

    def __init__(self, strategy: Strategy, *, max_rank: int | None = None) -> None:
        if max_rank is not None and max_rank < 1:
            msg = f"max_rank must be >= 1, got {max_rank}"
            raise ValueError(msg)
        self._strategy = strategy
        self._max_rank = max_rank

    @property
    def strategy(self) -> Strategy:
        return self._strategy

    @property
    def max_rank(self) -> int | None:
        return self._max_rank

    def evaluate(self, result: ScanResult) -> tuple[Signal, ...]:
        """Evaluate *result*, optionally filtering to top ranks first."""
        if self._max_rank is not None:
            filtered = result.top_n(self._max_rank)
            return self._strategy.evaluate(filtered)
        return self._strategy.evaluate(result)
