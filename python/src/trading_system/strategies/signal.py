"""Trading signal types and models."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from trading_system.models.symbol import Symbol


class SignalType(StrEnum):
    """Actionable signal produced by a strategy."""

    BUY = "BUY"
    HOLD = "HOLD"
    SELL = "SELL"
    IGNORE = "IGNORE"


@dataclass(frozen=True, slots=True)
class Signal:
    """A single trading signal for a symbol."""

    symbol: Symbol
    signal_type: SignalType
    reason: str
    rank: int = 0
    score: float = 0.0
