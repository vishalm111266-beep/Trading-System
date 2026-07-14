"""Tests for trading_system.indicators.relative_strength."""

from datetime import datetime, timedelta

import pytest
from trading_system.indicators.relative_strength import relative_strength
from trading_system.models.rs_signal import RSSignal

BASE = datetime(2025, 1, 1)


def _ts(n: int) -> datetime:
    return BASE + timedelta(days=n)


class TestRelativeStrength:
    def test_basic(self) -> None:
        stock = [100.0, 110.0, 105.0, 115.0]
        bench = [100.0, 105.0, 102.0, 108.0]
        ts = [_ts(i) for i in range(4)]
        signals = relative_strength(stock, bench, ts, lookback=1)
        assert len(signals) == 3
        for s in signals:
            assert isinstance(s, RSSignal)
            assert s.rs_value > 0

    def test_equal_returns_gives_rs_one(self) -> None:
        stock = [100.0, 110.0, 121.0]
        bench = [100.0, 110.0, 121.0]
        ts = [_ts(i) for i in range(3)]
        signals = relative_strength(stock, bench, ts, lookback=1)
        for s in signals:
            assert s.rs_value == pytest.approx(1.0)

    def test_stock_outperforms(self) -> None:
        stock = [100.0, 120.0]
        bench = [100.0, 110.0]
        ts = [_ts(0), _ts(1)]
        signals = relative_strength(stock, bench, ts, lookback=1)
        assert signals[0].rs_value > 1.0

    def test_length_mismatch(self) -> None:
        with pytest.raises(ValueError, match="length mismatch"):
            relative_strength([1, 2], [1], [_ts(0), _ts(1)])

    def test_lookback_too_large(self) -> None:
        with pytest.raises(ValueError, match="need at least"):
            relative_strength([1, 2], [1, 2], [_ts(0), _ts(1)], lookback=5)

    def test_invalid_lookback(self) -> None:
        with pytest.raises(ValueError, match="lookback"):
            relative_strength([1, 2, 3], [1, 2, 3], [_ts(0), _ts(1), _ts(2)], lookback=0)

    def test_benchmark_zero_return(self) -> None:
        stock = [100.0, 110.0]
        bench = [100.0, 100.0]
        ts = [_ts(0), _ts(1)]
        with pytest.raises(ValueError, match="benchmark return is zero"):
            relative_strength(stock, bench, ts, lookback=1)


class TestRSSignal:
    def test_zero_benchmark_raises(self) -> None:
        with pytest.raises(ValueError, match="benchmark_return"):
            RSSignal(timestamp=_ts(0), stock_return=0.1, benchmark_return=0.0, rs_value=1.0)

    def test_negative_rs_raises(self) -> None:
        with pytest.raises(ValueError, match="rs_value"):
            RSSignal(timestamp=_ts(0), stock_return=0.1, benchmark_return=0.1, rs_value=-1.0)
