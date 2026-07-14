"""Tests for trading_system.strategies.rules."""

import pytest
from trading_system.models.ranking_result import RankedSymbol, RankingResult
from trading_system.models.symbol import Symbol
from trading_system.scanner.result import ScanDetail, ScanResult
from trading_system.strategies.rules import (
    MansfieldRSRule,
    ReturnRule,
    RSRankRule,
    RSValueRule,
)
from trading_system.strategies.signal import SignalType


def _detail(
    symbol: str = "AAPL",
    rs_value: float = 2.0,
    stock_return: float = 0.10,
    benchmark_return: float = 0.05,
    mansfield_rs: float | None = None,
) -> ScanDetail:
    return ScanDetail(
        symbol=Symbol(raw=symbol),
        rs_value=rs_value,
        stock_return=stock_return,
        benchmark_return=benchmark_return,
        mansfield_rs=mansfield_rs,
    )


def _result(*symbols: str, scores: list[float] | None = None) -> ScanResult:
    if scores is None:
        scores = [2.0] * len(symbols)
    ranking = RankingResult(
        entries=tuple(
            RankedSymbol(symbol=Symbol(raw=s), rank=i + 1, score=sc)
            for i, (s, sc) in enumerate(zip(symbols, scores, strict=True))
        )
    )
    details = tuple(
        ScanDetail(
            symbol=Symbol(raw=s),
            rs_value=sc,
            stock_return=sc * 0.05,
            benchmark_return=0.05,
        )
        for s, sc in zip(symbols, scores, strict=True)
    )
    return ScanResult(ranking=ranking, details=details)


class TestRSRankRule:
    def test_within_top_n(self) -> None:
        rule = RSRankRule(top_n=3)
        detail = _detail(symbol="AAPL")
        result = _result("AAPL", "MSFT", "GOOG", scores=[3.0, 2.0, 1.0])
        sig, reason = rule.evaluate(detail, result)
        assert sig is SignalType.BUY
        assert "rank 1" in reason

    def test_outside_top_n(self) -> None:
        rule = RSRankRule(top_n=2)
        detail = _detail(symbol="GOOG")
        result = _result("AAPL", "MSFT", "GOOG", scores=[3.0, 2.0, 1.0])
        sig, reason = rule.evaluate(detail, result)
        assert sig is SignalType.HOLD
        assert "rank 3" in reason

    def test_custom_signal(self) -> None:
        rule = RSRankRule(top_n=5, signal=SignalType.IGNORE)
        detail = _detail(symbol="AAPL")
        result = _result("AAPL", scores=[1.0])
        sig, _reason = rule.evaluate(detail, result)
        assert sig is SignalType.IGNORE

    def test_symbol_not_in_ranking(self) -> None:
        rule = RSRankRule(top_n=1)
        detail = _detail(symbol="MISSING")
        result = _result("AAPL", scores=[1.0])
        sig, _reason = rule.evaluate(detail, result)
        assert sig is SignalType.HOLD

    def test_invalid_top_n(self) -> None:
        with pytest.raises(ValueError, match="top_n must be >= 1"):
            RSRankRule(top_n=0)


class TestRSValueRule:
    def test_above_threshold(self) -> None:
        rule = RSValueRule(min_rs=1.5)
        detail = _detail(rs_value=2.0)
        result = _result("AAPL")
        sig, reason = rule.evaluate(detail, result)
        assert sig is SignalType.BUY
        assert "2.0" in reason
        assert "1.5" in reason

    def test_below_threshold(self) -> None:
        rule = RSValueRule(min_rs=1.5)
        detail = _detail(rs_value=1.0)
        result = _result("AAPL")
        sig, _reason = rule.evaluate(detail, result)
        assert sig is SignalType.HOLD

    def test_exact_threshold(self) -> None:
        rule = RSValueRule(min_rs=2.0)
        detail = _detail(rs_value=2.0)
        result = _result("AAPL")
        sig, _reason = rule.evaluate(detail, result)
        assert sig is SignalType.BUY

    def test_custom_signal(self) -> None:
        rule = RSValueRule(min_rs=0.5, signal=SignalType.IGNORE)
        detail = _detail(rs_value=1.0)
        result = _result("AAPL")
        sig, _reason = rule.evaluate(detail, result)
        assert sig is SignalType.IGNORE


class TestMansfieldRSRule:
    def test_positive(self) -> None:
        rule = MansfieldRSRule()
        detail = _detail(mansfield_rs=5.0)
        result = _result("AAPL")
        sig, reason = rule.evaluate(detail, result)
        assert sig is SignalType.BUY
        assert "> 0" in reason

    def test_negative(self) -> None:
        rule = MansfieldRSRule()
        detail = _detail(mansfield_rs=-3.0)
        result = _result("AAPL")
        sig, reason = rule.evaluate(detail, result)
        assert sig is SignalType.SELL
        assert "< 0" in reason

    def test_zero(self) -> None:
        rule = MansfieldRSRule()
        detail = _detail(mansfield_rs=0.0)
        result = _result("AAPL")
        sig, _reason = rule.evaluate(detail, result)
        assert sig is SignalType.HOLD

    def test_none(self) -> None:
        rule = MansfieldRSRule()
        detail = _detail(mansfield_rs=None)
        result = _result("AAPL")
        sig, _reason = rule.evaluate(detail, result)
        assert sig is SignalType.HOLD

    def test_custom_signals(self) -> None:
        rule = MansfieldRSRule(positive_signal=SignalType.IGNORE, negative_signal=SignalType.HOLD)
        result = _result("AAPL")
        assert rule.evaluate(_detail(mansfield_rs=1.0), result)[0] is SignalType.IGNORE
        assert rule.evaluate(_detail(mansfield_rs=-1.0), result)[0] is SignalType.HOLD


class TestReturnRule:
    def test_above_min(self) -> None:
        rule = ReturnRule(min_return=0.05)
        detail = _detail(stock_return=0.10)
        result = _result("AAPL")
        sig, reason = rule.evaluate(detail, result)
        assert sig is SignalType.BUY
        assert "0.1" in reason

    def test_below_max(self) -> None:
        rule = ReturnRule(max_return=-0.05)
        detail = _detail(stock_return=-0.10)
        result = _result("AAPL")
        sig, reason = rule.evaluate(detail, result)
        assert sig is SignalType.SELL
        assert "-0.1" in reason

    def test_in_neutral_zone(self) -> None:
        rule = ReturnRule(min_return=0.10, max_return=-0.10)
        detail = _detail(stock_return=0.02)
        result = _result("AAPL")
        sig, _reason = rule.evaluate(detail, result)
        assert sig is SignalType.HOLD

    def test_exact_min(self) -> None:
        rule = ReturnRule(min_return=0.10)
        detail = _detail(stock_return=0.10)
        result = _result("AAPL")
        sig, _reason = rule.evaluate(detail, result)
        assert sig is SignalType.BUY

    def test_exact_max(self) -> None:
        rule = ReturnRule(max_return=-0.10)
        detail = _detail(stock_return=-0.10)
        result = _result("AAPL")
        sig, _reason = rule.evaluate(detail, result)
        assert sig is SignalType.SELL

    def test_custom_signals(self) -> None:
        rule = ReturnRule(min_return=0.05, buy_signal=SignalType.IGNORE)
        detail = _detail(stock_return=0.10)
        result = _result("AAPL")
        sig, _reason = rule.evaluate(detail, result)
        assert sig is SignalType.IGNORE
