"""Aggregated market data container."""

from __future__ import annotations

from dataclasses import dataclass, field

from trading_system.models.candle import Candle
from trading_system.models.symbol import Symbol


@dataclass(frozen=True, slots=True)
class MarketData:
    """Ordered candle series for a single symbol."""

    symbol: Symbol
    candles: tuple[Candle, ...] = field(default_factory=tuple)

    @property
    def empty(self) -> bool:
        return len(self.candles) == 0

    @property
    def length(self) -> int:
        return len(self.candles)
