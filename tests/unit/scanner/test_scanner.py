"""Tests for trading_system.scanner.scanner."""

from datetime import datetime, timedelta

import pytest
from trading_system.models.candle import Candle
from trading_system.models.market_data import MarketData
from trading_system.models.symbol import Symbol
from trading_system.scanner.filters import has_sufficient_data
from trading_system.scanner.scanner import RSScanner

BASE = datetime(2025, 1, 1)


def _ts(n: int) -> datetime:
    return BASE + timedelta(days=n)


def _candle(close: float, ts: int) -> Candle:
    return Candle(timestamp=_ts(ts), open=close, high=close, low=close, close=close, volume=100.0)


def _make_data(symbol: str, closes: list[float]) -> MarketData:
    return MarketData(
        symbol=Symbol(raw=symbol),
        candles=tuple(_candle(c, i) for i, c in enumerate(closes)),
    )


def _benchmark() -> MarketData:
    return _make_data("SPX", [100.0, 105.0, 110.25, 115.7625])


def _outperformer() -> MarketData:
    return _make_data("AAPL", [100.0, 110.0, 121.0, 133.1])


def _inliner() -> MarketData:
    return _make_data("MSFT", [100.0, 105.0, 110.25, 115.7625])


class TestRSScannerInit:
    def test_defaults(self) -> None:
        s = RSScanner()
        assert s.lookback == 252
        assert s.ma_period == 50

    def test_custom(self) -> None:
        s = RSScanner(lookback=10, ma_period=5)
        assert s.lookback == 10
        assert s.ma_period == 5

    def test_invalid_lookback(self) -> None:
        with pytest.raises(ValueError, match="lookback must be >= 1"):
            RSScanner(lookback=0)

    def test_invalid_ma_period(self) -> None:
        with pytest.raises(ValueError, match="ma_period must be >= 1"):
            RSScanner(ma_period=0)


class TestRSScannerScan:
    def test_empty_stocks(self) -> None:
        scanner = RSScanner(lookback=1, ma_period=2)
        result = scanner.scan([], _benchmark())
        assert result.empty

    def test_empty_benchmark(self) -> None:
        scanner = RSScanner(lookback=1, ma_period=2)
        stocks = [_outperformer()]
        empty_bench = MarketData(symbol=Symbol(raw="SPX"))
        with pytest.raises(ValueError, match="benchmark cannot be empty"):
            scanner.scan(stocks, empty_bench)

    def test_single_stock(self) -> None:
        scanner = RSScanner(lookback=1, ma_period=2)
        result = scanner.scan([_outperformer()], _benchmark())
        assert result.length == 1
        assert result.ranking.entries[0].symbol.raw == "AAPL"
        assert result.ranking.entries[0].score == pytest.approx(2.0)
        assert result.benchmark_symbol.raw == "SPX"
        assert result.lookback == 1
        assert result.ma_period == 2

    def test_multiple_stocks_ranked(self) -> None:
        scanner = RSScanner(lookback=1, ma_period=2)
        result = scanner.scan([_inliner(), _outperformer()], _benchmark())
        assert result.length == 2
        assert result.ranking.entries[0].symbol.raw == "AAPL"
        assert result.ranking.entries[0].score == pytest.approx(2.0)
        assert result.ranking.entries[1].symbol.raw == "MSFT"
        assert result.ranking.entries[1].score == pytest.approx(1.0)

    def test_details_match_ranking(self) -> None:
        scanner = RSScanner(lookback=1, ma_period=2)
        result = scanner.scan([_inliner(), _outperformer()], _benchmark())
        assert len(result.details) == result.length
        for entry in result.ranking.entries:
            detail = next(d for d in result.details if d.symbol == entry.symbol)
            assert detail.rs_value == pytest.approx(entry.score)

    def test_insufficient_data_stock_skipped(self) -> None:
        short_stock = _make_data("SHORT", [100.0, 110.0])
        scanner = RSScanner(lookback=5, ma_period=2)
        result = scanner.scan([short_stock], _benchmark())
        assert result.empty

    def test_no_overlapping_timestamps(self) -> None:
        future_candles = tuple(
            Candle(
                timestamp=_ts(100 + i),
                open=c,
                high=c,
                low=c,
                close=c,
                volume=100.0,
            )
            for i, c in enumerate([100.0, 110.0, 121.0, 133.1])
        )
        future_data = MarketData(symbol=Symbol(raw="FUT"), candles=future_candles)
        scanner = RSScanner(lookback=1, ma_period=2)
        result = scanner.scan([future_data], _benchmark())
        assert result.empty

    def test_filters_applied(self) -> None:
        short = _make_data("SHORT", [100.0])
        long_stock = _outperformer()
        scanner = RSScanner(lookback=1, ma_period=2)
        result = scanner.scan(
            [short, long_stock],
            _benchmark(),
            filters=[has_sufficient_data(min_candles=4)],
        )
        assert result.length == 1
        assert result.ranking.entries[0].symbol.raw == "AAPL"

    def test_all_filtered_out(self) -> None:
        short = _make_data("SHORT", [100.0])
        scanner = RSScanner(lookback=1, ma_period=2)
        result = scanner.scan(
            [short],
            _benchmark(),
            filters=[has_sufficient_data(min_candles=10)],
        )
        assert result.empty

    def test_mansfield_rs_present(self) -> None:
        scanner = RSScanner(lookback=1, ma_period=2)
        result = scanner.scan([_outperformer()], _benchmark())
        assert len(result.details) == 1
        assert result.details[0].mansfield_rs is not None
        assert result.details[0].mansfield_rs == pytest.approx(0.0)

    def test_stock_return_values(self) -> None:
        scanner = RSScanner(lookback=1, ma_period=2)
        result = scanner.scan([_outperformer()], _benchmark())
        detail = result.details[0]
        assert detail.stock_return == pytest.approx(0.10)
        assert detail.benchmark_return == pytest.approx(0.05)
        assert detail.rs_value == pytest.approx(2.0)
