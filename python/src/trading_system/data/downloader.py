"""Download orchestration."""

from __future__ import annotations

import logging
from datetime import datetime

from trading_system.data.cache import Cache
from trading_system.data.provider import Provider
from trading_system.data.validator import validate_candles
from trading_system.models.candle import Candle
from trading_system.models.symbol import Symbol

logger = logging.getLogger(__name__)


class Downloader:
    """Coordinate fetching data from a provider with validation and caching."""

    def __init__(self, provider: Provider, cache: Cache) -> None:
        self._provider = provider
        self._cache = cache

    @property
    def provider(self) -> Provider:
        return self._provider

    def download(
        self,
        symbol: Symbol,
        start: datetime,
        end: datetime,
        *,
        force: bool = False,
    ) -> list[Candle]:
        """Fetch, validate, and cache candles for a date range."""
        if not force:
            cached = self._cache.get(symbol, start, end)
            if cached is not None:
                logger.debug("cache hit for %s", symbol)
                return cached

        logger.debug("downloading %s from %s", symbol, self._provider.name)
        candles = self._provider.fetch_candles(symbol, start, end)
        validated = validate_candles(candles)
        self._cache.put(symbol, start, end, validated)
        return validated
