"""Ranking result model."""

from __future__ import annotations

from dataclasses import dataclass, field

from trading_system.models.symbol import Symbol


@dataclass(frozen=True, slots=True)
class RankedSymbol:
    """A symbol with its rank and score."""

    symbol: Symbol
    rank: int
    score: float


@dataclass(frozen=True, slots=True)
class RankingResult:
    """Ordered list of ranked symbols."""

    entries: tuple[RankedSymbol, ...] = field(default_factory=tuple)

    @property
    def empty(self) -> bool:
        return len(self.entries) == 0

    @property
    def length(self) -> int:
        return len(self.entries)

    def top_n(self, n: int) -> RankingResult:
        """Return a new result containing only the top *n* entries."""
        if n < 0:
            msg = f"n must be non-negative, got {n}"
            raise ValueError(msg)
        return RankingResult(entries=self.entries[:n])
