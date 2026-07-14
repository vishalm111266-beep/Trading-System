"""Tests for trading_system.indicators.mansfield_rs."""

from datetime import datetime, timedelta

import pytest
from trading_system.indicators.mansfield_rs import mansfield_rs

BASE = datetime(2025, 1, 1)


def _ts(n: int) -> datetime:
    return BASE + timedelta(days=n)


class TestMansfieldRS:
    def test_basic(self) -> None:
        stock = [100 + i for i in range(60)]
        bench = [100 + i * 0.5 for i in range(60)]
        ts = [_ts(i) for i in range(60)]
        result = mansfield_rs(stock, bench, ts, lookback=1, ma_period=10)
        assert len(result) == 60
        non_none = [v for v in result if v is not None]
        assert len(non_none) > 0

    def test_outperformer_positive(self) -> None:
        stock = [100 + i * i * 0.1 for i in range(60)]
        bench = [100 + i for i in range(60)]
        ts = [_ts(i) for i in range(60)]
        result = mansfield_rs(stock, bench, ts, lookback=1, ma_period=10)
        final = [v for v in result if v is not None]
        assert len(final) > 0
        assert any(v > 0 for v in final)

    def test_invalid_lookback(self) -> None:
        with pytest.raises(ValueError, match="lookback"):
            mansfield_rs([1, 2, 3], [1, 2, 3], [_ts(0), _ts(1), _ts(2)], lookback=0)

    def test_invalid_ma_period(self) -> None:
        with pytest.raises(ValueError, match="ma_period"):
            mansfield_rs([1, 2, 3], [1, 2, 3], [_ts(0), _ts(1), _ts(2)], ma_period=0)
