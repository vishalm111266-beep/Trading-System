"""Relative strength scanner that ranks stocks against a benchmark."""

from __future__ import annotations

import logging
from collections.abc import Sequence

from trading_system.indicators.mansfield_rs import mansfield_rs
from trading_system.indicators.ranking import rank_by_rs
from trading_system.indicators.relative_strength import relative_strength
from trading_system.models.market_data import MarketData
from trading_system.models.ranking_result import RankingResult
from trading_system.models.symbol import Symbol
from trading_system.scanner.filters import Filter
from trading_system.scanner.result import ScanDetail, ScanResult

logger = logging.getLogger(__name__)


class RSScanner:
    """Evaluates stocks by relative strength against a benchmark."""

    def __init__(self, lookback: int = 252, ma_period: int = 50) -> None:
        if lookback < 1:
            msg = f"lookback must be >= 1, got {lookback}"
            raise ValueError(msg)
        if ma_period < 1:
            msg = f"ma_period must be >= 1, got {ma_period}"
            raise ValueError(msg)
        self._lookback = lookback
        self._ma_period = ma_period

    @property
    def lookback(self) -> int:
        return self._lookback

    @property
    def ma_period(self) -> int:
        return self._ma_period

    def scan(
        self,
        stocks: Sequence[MarketData],
        benchmark: MarketData,
        *,
        filters: Sequence[Filter] | None = None,
    ) -> ScanResult:
        """Scan stocks against *benchmark* and return ranked results."""
        if not stocks:
            return ScanResult(
                ranking=RankingResult(),
                benchmark_symbol=benchmark.symbol,
                lookback=self._lookback,
                ma_period=self._ma_period,
            )

        if benchmark.empty:
            msg = "benchmark cannot be empty"
            raise ValueError(msg)

        applied_filters = list(filters) if filters else []
        benchmark_prices = [c.close for c in benchmark.candles]
        benchmark_timestamps = [c.timestamp for c in benchmark.candles]

        results: list[tuple[Symbol, float, ScanDetail]] = []

        for stock_data in stocks:
            if not self._passes_filters(stock_data, applied_filters):
                continue
            detail = self._compute_rs(stock_data, benchmark_prices, benchmark_timestamps)
            if detail is not None:
                results.append((stock_data.symbol, detail.rs_value, detail))

        if not results:
            return ScanResult(
                ranking=RankingResult(),
                benchmark_symbol=benchmark.symbol,
                lookback=self._lookback,
                ma_period=self._ma_period,
            )

        results.sort(key=lambda r: r[1], reverse=True)

        symbols = [r[0] for r in results]
        scores = [r[1] for r in results]
        details = tuple(r[2] for r in results)

        ranking = rank_by_rs(symbols, scores)

        return ScanResult(
            ranking=ranking,
            details=details,
            benchmark_symbol=benchmark.symbol,
            lookback=self._lookback,
            ma_period=self._ma_period,
        )

    def _passes_filters(self, data: MarketData, filters: list[Filter]) -> bool:
        return all(f(data) for f in filters)

    def _compute_rs(
        self,
        stock_data: MarketData,
        benchmark_prices: list[float],
        benchmark_timestamps: list,
    ) -> ScanDetail | None:
        stock_prices = [c.close for c in stock_data.candles]
        stock_timestamps = [c.timestamp for c in stock_data.candles]

        common_ts = sorted(set(stock_timestamps) & set(benchmark_timestamps))
        if len(common_ts) < self._lookback + 1:
            logger.debug(
                "insufficient common data for %s: %d points",
                stock_data.symbol,
                len(common_ts),
            )
            return None

        stock_map = dict(zip(stock_timestamps, stock_prices, strict=True))
        bench_map = dict(zip(benchmark_timestamps, benchmark_prices, strict=True))

        aligned_stock = [stock_map[t] for t in common_ts]
        aligned_bench = [bench_map[t] for t in common_ts]

        try:
            rs_signals = relative_strength(aligned_stock, aligned_bench, common_ts, self._lookback)
        except ValueError:
            logger.debug("RS computation failed for %s", stock_data.symbol)
            return None

        if not rs_signals:
            return None

        latest = rs_signals[-1]

        latest_mansfield: float | None = None
        try:
            mansfield_values = mansfield_rs(
                aligned_stock, aligned_bench, common_ts, self._lookback, self._ma_period
            )
            for val in reversed(mansfield_values):
                if val is not None:
                    latest_mansfield = val
                    break
        except ValueError:
            logger.debug("Mansfield RS failed for %s", stock_data.symbol)

        return ScanDetail(
            symbol=stock_data.symbol,
            rs_value=latest.rs_value,
            stock_return=latest.stock_return,
            benchmark_return=latest.benchmark_return,
            mansfield_rs=latest_mansfield,
        )
