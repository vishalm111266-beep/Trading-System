"""Portfolio allocation framework."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from trading_system.models.symbol import Symbol


class AllocationMethod(StrEnum):
    """Method used to allocate capital across positions."""

    EQUAL_WEIGHT = "EQUAL_WEIGHT"
    SCORE_WEIGHTED = "SCORE_WEIGHTED"
    RANK_WEIGHTED = "RANK_WEIGHTED"


@dataclass(frozen=True, slots=True)
class Allocation:
    """Capital allocation for a single symbol."""

    symbol: Symbol
    weight: float
    dollar_amount: float


class PortfolioAllocator:
    """Allocates portfolio capital across ranked symbols."""

    def __init__(
        self,
        method: AllocationMethod = AllocationMethod.EQUAL_WEIGHT,
        max_positions: int = 10,
        min_weight: float = 0.0,
    ) -> None:
        if max_positions < 1:
            msg = f"max_positions must be >= 1, got {max_positions}"
            raise ValueError(msg)
        if min_weight < 0 or min_weight >= 1:
            msg = f"min_weight must be in [0, 1), got {min_weight}"
            raise ValueError(msg)
        self.method = method
        self.max_positions = max_positions
        self.min_weight = min_weight

    def allocate(
        self,
        equity: float,
        symbols: list[Symbol],
        scores: list[float],
    ) -> list[Allocation]:
        """Compute allocations for the given symbols.

        Parameters
        ----------
        equity:
            Total portfolio equity.
        symbols:
            Ordered list of symbols to allocate to.
        scores:
            Corresponding scores (higher = better).
        """
        if len(symbols) != len(scores):
            msg = f"symbols and scores must have same length, got {len(symbols)} vs {len(scores)}"
            raise ValueError(msg)
        if equity <= 0:
            msg = f"equity must be positive, got {equity}"
            raise ValueError(msg)

        n = min(len(symbols), self.max_positions)
        if n == 0:
            return []

        trimmed_symbols = symbols[:n]
        trimmed_scores = scores[:n]

        weights = self._compute_weights(trimmed_scores)

        allocations: list[Allocation] = []
        for sym, w in zip(trimmed_symbols, weights, strict=True):
            allocations.append(Allocation(symbol=sym, weight=w, dollar_amount=equity * w))
        return allocations

    def _compute_weights(self, scores: list[float]) -> list[float]:
        if self.method == AllocationMethod.EQUAL_WEIGHT:
            return self._equal_weight(len(scores))
        if self.method == AllocationMethod.SCORE_WEIGHTED:
            return self._score_weighted(scores)
        return self._rank_weighted(len(scores))

    def _equal_weight(self, n: int) -> list[float]:
        w = 1.0 / n
        return [w] * n

    def _score_weighted(self, scores: list[float]) -> list[float]:
        n = len(scores)
        total = sum(scores)
        if total <= 0:
            return self._equal_weight(n)
        weights = [s / total for s in scores]
        if self.min_weight > 0:
            weights = self._enforce_min_weight(weights)
        return weights

    def _enforce_min_weight(self, weights: list[float]) -> list[float]:
        n = len(weights)
        result = list(weights)
        for _ in range(10):
            clamped = [max(self.min_weight, w) for w in result]
            total_w = sum(clamped)
            if total_w <= 0:
                return self._equal_weight(n)
            result = [w / total_w for w in clamped]
            if all(w >= self.min_weight - 1e-9 for w in result):
                break
        else:
            return self._equal_weight(n)
        return result

    def _rank_weighted(self, n: int) -> list[float]:
        denom = n * (n + 1) / 2.0
        weights = [(n - i) / denom for i in range(n)]
        return [max(self.min_weight, w) for w in weights]
