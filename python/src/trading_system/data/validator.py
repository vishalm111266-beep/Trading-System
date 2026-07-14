"""Candle data validation utilities."""

from __future__ import annotations

from trading_system.data.exceptions import ValidationError
from trading_system.models.candle import Candle


def validate_candle(candle: Candle) -> None:
    """Raise ``ValidationError`` if *candle* is inconsistent."""
    if candle.high < candle.low:
        msg = f"high ({candle.high}) < low ({candle.low})"
        raise ValidationError(msg)
    if candle.open < candle.low or candle.open > candle.high:
        msg = f"open ({candle.open}) outside [{candle.low}, {candle.high}]"
        raise ValidationError(msg)
    if candle.close < candle.low or candle.close > candle.high:
        msg = f"close ({candle.close}) outside [{candle.low}, {candle.high}]"
        raise ValidationError(msg)
    if candle.volume < 0:
        msg = f"negative volume: {candle.volume}"
        raise ValidationError(msg)


def validate_candles(candles: list[Candle]) -> list[Candle]:
    """Validate every candle and return the list unchanged."""
    for c in candles:
        validate_candle(c)
    return candles
