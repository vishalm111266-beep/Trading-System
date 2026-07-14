"""Tests for trading_system.scanner.pipeline."""

from datetime import datetime, timedelta

from trading_system.models.candle import Candle
from trading_system.models.market_data import MarketData
from trading_system.models.symbol import Symbol
from trading_system.scanner.filters import has_sufficient_data, is_active
from trading_system.scanner.pipeline import ScanPipeline

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


class TestScanPipelineInit:
    def test_defaults(self) -> None:
        p = ScanPipeline()
        assert p.scanner.lookback == 252
        assert p.scanner.ma_period == 50
        assert p.filters == []

    def test_custom_config(self) -> None:
        p = ScanPipeline(lookback=10, ma_period=5)
        assert p.scanner.lookback == 10
        assert p.scanner.ma_period == 5

    def test_initial_filters(self) -> None:
        p = ScanPipeline(filters=[is_active()])
        assert len(p.filters) == 1

    def test_add_filter(self) -> None:
        p = ScanPipeline()
        p.add_filter(is_active())
        p.add_filter(has_sufficient_data(min_candles=2))
        assert len(p.filters) == 2


class TestScanPipelineRun:
    def test_basic_run(self) -> None:
        p = ScanPipeline(lookback=1, ma_period=2)
        result = p.run([_inliner(), _outperformer()], _benchmark())
        assert result.length == 2
        assert result.ranking.entries[0].symbol.raw == "AAPL"

    def test_filters_applied(self) -> None:
        p = ScanPipeline(lookback=1, ma_period=2)
        p.add_filter(has_sufficient_data(min_candles=4))
        short = _make_data("SHORT", [100.0])
        result = p.run([short, _outperformer()], _benchmark())
        assert result.length == 1
        assert result.ranking.entries[0].symbol.raw == "AAPL"

    def test_all_filtered(self) -> None:
        p = ScanPipeline(lookback=1, ma_period=2)
        p.add_filter(has_sufficient_data(min_candles=100))
        result = p.run([_outperformer()], _benchmark())
        assert result.empty

    def test_empty_stocks(self) -> None:
        p = ScanPipeline(lookback=1, ma_period=2)
        result = p.run([], _benchmark())
        assert result.empty

    def test_multiple_filters(self) -> None:
        p = ScanPipeline(lookback=1, ma_period=2)
        p.add_filter(is_active())
        p.add_filter(has_sufficient_data(min_candles=4))
        result = p.run([_outperformer()], _benchmark())
        assert result.length == 1
