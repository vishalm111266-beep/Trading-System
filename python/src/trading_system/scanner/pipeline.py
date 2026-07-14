"""Orchestrates scanning with composable filters."""

from __future__ import annotations

from collections.abc import Sequence

from trading_system.models.market_data import MarketData
from trading_system.scanner.filters import Filter
from trading_system.scanner.result import ScanResult
from trading_system.scanner.scanner import RSScanner


class ScanPipeline:
    """Chains filter application with RS scanning."""

    def __init__(
        self,
        lookback: int = 252,
        ma_period: int = 50,
        filters: Sequence[Filter] | None = None,
    ) -> None:
        self._scanner = RSScanner(lookback=lookback, ma_period=ma_period)
        self._filters: list[Filter] = list(filters) if filters else []

    @property
    def scanner(self) -> RSScanner:
        return self._scanner

    @property
    def filters(self) -> list[Filter]:
        return list(self._filters)

    def add_filter(self, filter_fn: Filter) -> None:
        """Append a filter to the pipeline."""
        self._filters.append(filter_fn)

    def run(
        self,
        stocks: Sequence[MarketData],
        benchmark: MarketData,
    ) -> ScanResult:
        """Run the full scan pipeline."""
        return self._scanner.scan(stocks, benchmark, filters=self._filters)
