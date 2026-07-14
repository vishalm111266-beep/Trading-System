"""High-level data loader combining source, validation, and cache."""

from __future__ import annotations

import logging
from datetime import datetime

from trading_system.data.cache import Cache
from trading_system.data.datasource import DataSource
from trading_system.data.validator import validate_candles
from trading_system.models.candle import Candle
from trading_system.models.symbol import Symbol

logger = logging.getLogger(__name__)


class Loader:
    """Load candles with caching and validation."""

    def __init__(self, source: DataSource, cache: Cache) -> None:
        self._source = source
        self._cache = cache

    def load(
        self,
        symbol: Symbol,
        start: datetime,
        end: datetime,
        *,
        force_refresh: bool = False,
    ) -> list[Candle]:
        """Fetch candles, using cache when available."""
        if not force_refresh:
            cached = self._cache.get(symbol, start, end)
            if cached is not None:
                logger.debug("cache hit for %s", symbol)
                return cached

        logger.debug("fetching %s from source", symbol)
        candles = self._source.fetch_candles(symbol, start, end)
        validated = validate_candles(candles)
        self._cache.put(symbol, start, end, validated)
        return validated
