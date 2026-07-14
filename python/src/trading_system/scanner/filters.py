"""Composable filters for market data screening."""

from __future__ import annotations

from collections.abc import Callable

from trading_system.models.market_data import MarketData

type Filter = Callable[[MarketData], bool]


def has_sufficient_data(min_candles: int = 1) -> Filter:
    """Return a filter that rejects stocks with fewer than *min_candles*."""
    if min_candles < 1:
        msg = f"min_candles must be >= 1, got {min_candles}"
        raise ValueError(msg)

    def _filter(data: MarketData) -> bool:
        return data.length >= min_candles

    return _filter


def has_valid_close_prices() -> Filter:
    """Return a filter that rejects stocks with non-positive close prices."""

    def _filter(data: MarketData) -> bool:
        if data.empty:
            return False
        return all(candle.close > 0 for candle in data.candles)

    return _filter


def is_active() -> Filter:
    """Return a filter that rejects empty datasets."""

    def _filter(data: MarketData) -> bool:
        return not data.empty

    return _filter
