"""Tests for trading_system.indicators.moving_average."""

import pytest
from trading_system.indicators.moving_average import ema, sma


class TestSMA:
    def test_basic(self) -> None:
        result = sma([1, 2, 3, 4, 5], 3)
        assert result[:2] == [None, None]
        assert result[2] == pytest.approx(2.0)
        assert result[3] == pytest.approx(3.0)
        assert result[4] == pytest.approx(4.0)

    def test_period_one(self) -> None:
        result = sma([10, 20, 30], 1)
        assert result == pytest.approx([10.0, 20.0, 30.0])

    def test_period_equals_length(self) -> None:
        result = sma([1, 2, 3], 3)
        assert result[:2] == [None, None]
        assert result[2] == pytest.approx(2.0)

    def test_single_value(self) -> None:
        result = sma([5], 1)
        assert result == pytest.approx([5.0])

    def test_invalid_period(self) -> None:
        with pytest.raises(ValueError, match="period"):
            sma([1, 2], 0)


class TestEMA:
    def test_basic(self) -> None:
        result = ema([1, 2, 3, 4, 5], 3)
        assert result[:2] == [None, None]
        assert result[2] == pytest.approx(2.0)
        assert result[3] is not None
        assert result[4] is not None
        assert result[3] > result[2]

    def test_period_one(self) -> None:
        result = ema([10, 20, 30], 1)
        assert result[0] == pytest.approx(10.0)
        assert result[1] == pytest.approx(20.0)
        assert result[2] == pytest.approx(30.0)

    def test_insufficient_data(self) -> None:
        result = ema([1, 2], 5)
        assert result == [None, None]

    def test_invalid_period(self) -> None:
        with pytest.raises(ValueError, match="period"):
            ema([1, 2], 0)
