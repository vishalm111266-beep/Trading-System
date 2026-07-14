"""Tests for trading_system.scanner.filters."""

from datetime import datetime, timedelta

import pytest
from trading_system.models.candle import Candle
from trading_system.models.market_data import MarketData
from trading_system.models.symbol import Symbol
from trading_system.scanner.filters import (
    has_sufficient_data,
    has_valid_close_prices,
    is_active,
)

BASE = datetime(2025, 1, 1)


def _ts(n: int) -> datetime:
    return BASE + timedelta(days=n)


def _candle(close: float, ts: int = 0) -> Candle:
    return Candle(timestamp=_ts(ts), open=close, high=close, low=close, close=close, volume=100.0)


def _market_data(closes: list[float]) -> MarketData:
    return MarketData(
        symbol=Symbol(raw="TEST"),
        candles=tuple(_candle(c, i) for i, c in enumerate(closes)),
    )


class TestHasSufficientData:
    def test_pass(self) -> None:
        data = _market_data([100.0, 110.0, 120.0])
        f = has_sufficient_data(min_candles=3)
        assert f(data) is True

    def test_fail(self) -> None:
        data = _market_data([100.0])
        f = has_sufficient_data(min_candles=3)
        assert f(data) is False

    def test_exact_boundary(self) -> None:
        data = _market_data([100.0, 110.0])
        f = has_sufficient_data(min_candles=2)
        assert f(data) is True

    def test_empty_data(self) -> None:
        data = MarketData(symbol=Symbol(raw="X"))
        f = has_sufficient_data(min_candles=1)
        assert f(data) is False

    def test_default_min_candles(self) -> None:
        data = _market_data([100.0])
        f = has_sufficient_data()
        assert f(data) is True

    def test_invalid_min_candles(self) -> None:
        with pytest.raises(ValueError, match="min_candles must be >= 1"):
            has_sufficient_data(min_candles=0)


class TestHasValidClosePrices:
    def test_all_positive(self) -> None:
        data = _market_data([100.0, 200.0, 50.0])
        assert has_valid_close_prices()(data) is True

    def test_zero_price(self) -> None:
        data = _market_data([100.0, 0.0, 50.0])
        assert has_valid_close_prices()(data) is False

    def test_negative_price(self) -> None:
        data = _market_data([100.0, -10.0])
        assert has_valid_close_prices()(data) is False

    def test_empty_data(self) -> None:
        data = MarketData(symbol=Symbol(raw="X"))
        assert has_valid_close_prices()(data) is False


class TestIsActive:
    def test_non_empty(self) -> None:
        data = _market_data([100.0])
        assert is_active()(data) is True

    def test_empty(self) -> None:
        data = MarketData(symbol=Symbol(raw="X"))
        assert is_active()(data) is False
