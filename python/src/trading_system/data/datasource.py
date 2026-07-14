"""Abstract data-source interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from trading_system.models.candle import Candle
from trading_system.models.symbol import Symbol


class DataSource(ABC):
    """Base class for all market-data providers."""

    @abstractmethod
    def fetch_candles(
        self,
        symbol: Symbol,
        start: datetime,
        end: datetime,
    ) -> list[Candle]:
        """Return candles for *symbol* spanning ``[start, end]``."""
        ...
