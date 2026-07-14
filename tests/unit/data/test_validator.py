"""Tests for trading_system.data.validator."""

from datetime import datetime

import pytest
from trading_system.data.exceptions import ValidationError
from trading_system.data.validator import validate_candle, validate_candles
from trading_system.models.candle import Candle

TS = datetime(2025, 1, 1, 12, 0, 0)


def _good() -> Candle:
    return Candle(timestamp=TS, open=100.0, high=110.0, low=95.0, close=105.0, volume=1000)


class TestValidateCandle:
    def test_valid_candle_passes(self) -> None:
        validate_candle(_good())

    def test_high_lt_low_raises(self) -> None:
        c = Candle(timestamp=TS, open=100, high=90, low=95, close=100, volume=1)
        with pytest.raises(ValidationError, match="high"):
            validate_candle(c)

    def test_open_below_low_raises(self) -> None:
        c = Candle(timestamp=TS, open=90, high=110, low=95, close=100, volume=1)
        with pytest.raises(ValidationError, match="open"):
            validate_candle(c)

    def test_close_above_high_raises(self) -> None:
        c = Candle(timestamp=TS, open=100, high=110, low=95, close=115, volume=1)
        with pytest.raises(ValidationError, match="close"):
            validate_candle(c)

    def test_negative_volume_raises(self) -> None:
        c = Candle(timestamp=TS, open=100, high=110, low=95, close=100, volume=-1)
        with pytest.raises(ValidationError, match="negative volume"):
            validate_candle(c)


class TestValidateCandles:
    def test_multiple_valid(self) -> None:
        result = validate_candles([_good(), _good()])
        assert len(result) == 2

    def test_one_invalid_stops(self) -> None:
        bad = Candle(timestamp=TS, open=100, high=90, low=95, close=100, volume=1)
        with pytest.raises(ValidationError):
            validate_candles([_good(), bad])
