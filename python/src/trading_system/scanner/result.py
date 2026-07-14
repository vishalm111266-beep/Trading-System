"""Scanner result models."""

from __future__ import annotations

from dataclasses import dataclass, field

from trading_system.models.ranking_result import RankingResult
from trading_system.models.symbol import Symbol


@dataclass(frozen=True, slots=True)
class ScanDetail:
    """Per-stock RS scan detail."""

    symbol: Symbol
    rs_value: float
    stock_return: float
    benchmark_return: float
    mansfield_rs: float | None = None


@dataclass(frozen=True, slots=True)
class ScanResult:
    """Aggregated scan result with ranking and per-stock details."""

    ranking: RankingResult
    details: tuple[ScanDetail, ...] = field(default_factory=tuple)
    benchmark_symbol: Symbol = field(default_factory=lambda: Symbol(""))
    lookback: int = 0
    ma_period: int = 0

    @property
    def empty(self) -> bool:
        """Return True if result contains no entries."""
        return self.ranking.empty

    @property
    def length(self) -> int:
        """Return number of ranked entries."""
        return self.ranking.length

    def top_n(self, n: int) -> ScanResult:
        """Return a new result containing only the top *n* entries."""
        top_ranking = self.ranking.top_n(n)
        detail_map = {d.symbol: d for d in self.details}
        ordered_details = tuple(
            detail_map[entry.symbol] for entry in top_ranking.entries if entry.symbol in detail_map
        )
        return ScanResult(
            ranking=top_ranking,
            details=ordered_details,
            benchmark_symbol=self.benchmark_symbol,
            lookback=self.lookback,
            ma_period=self.ma_period,
        )
