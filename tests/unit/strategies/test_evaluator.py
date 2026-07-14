"""Tests for trading_system.strategies.evaluator and base.Strategy."""

import pytest
from trading_system.models.ranking_result import RankedSymbol, RankingResult
from trading_system.models.symbol import Symbol
from trading_system.scanner.result import ScanDetail, ScanResult
from trading_system.strategies.base import Strategy, StrategyRule
from trading_system.strategies.evaluator import StrategyEvaluator
from trading_system.strategies.rules import RSRankRule, RSValueRule
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


class _AlwaysBuy(StrategyRule):
    def evaluate(self, detail: ScanDetail, result: ScanResult) -> tuple[SignalType, str]:
        return SignalType.BUY, "always buy"


class _AlwaysHold(StrategyRule):
    def evaluate(self, detail: ScanDetail, result: ScanResult) -> tuple[SignalType, str]:
        return SignalType.HOLD, "always hold"


class _AlwaysIgnore(StrategyRule):
    def evaluate(self, detail: ScanDetail, result: ScanResult) -> tuple[SignalType, str]:
        return SignalType.IGNORE, "always ignore"


class TestStrategy:
    def test_no_rules_raises(self) -> None:
        with pytest.raises(ValueError, match="must have at least one rule"):
            Strategy([])

    def test_single_rule(self) -> None:
        strat = Strategy([_AlwaysBuy()])
        result = _result("AAPL", "MSFT")
        signals = strat.evaluate(result)
        assert len(signals) == 2
        assert all(s.signal_type is SignalType.BUY for s in signals)

    def test_first_non_hold_wins(self) -> None:
        strat = Strategy([_AlwaysHold(), _AlwaysBuy()])
        result = _result("AAPL")
        signals = strat.evaluate(result)
        assert signals[0].signal_type is SignalType.BUY
        assert signals[0].reason == "always buy"

    def test_all_hold(self) -> None:
        strat = Strategy([_AlwaysHold(), _AlwaysHold()])
        result = _result("AAPL")
        signals = strat.evaluate(result)
        assert signals[0].signal_type is SignalType.HOLD
        assert "all rules" in signals[0].reason

    def test_ignore_short_circuits(self) -> None:
        strat = Strategy([_AlwaysIgnore(), _AlwaysBuy()])
        result = _result("AAPL")
        signals = strat.evaluate(result)
        assert signals[0].signal_type is SignalType.IGNORE

    def test_rules_property(self) -> None:
        r1 = _AlwaysBuy()
        r2 = _AlwaysHold()
        strat = Strategy([r1, r2])
        assert len(strat.rules) == 2

    def test_missing_detail_returns_ignore(self) -> None:
        ranking = RankingResult(
            entries=(RankedSymbol(symbol=Symbol(raw="MISSING"), rank=1, score=1.0),)
        )
        result = ScanResult(ranking=ranking, details=())
        strat = Strategy([_AlwaysBuy()])
        signals = strat.evaluate(result)
        assert signals[0].signal_type is SignalType.IGNORE
        assert "no scan detail" in signals[0].reason


class TestStrategyEvaluator:
    def test_no_max_rank(self) -> None:
        strat = Strategy([RSRankRule(top_n=1)])
        evaluator = StrategyEvaluator(strat)
        result = _result("AAPL", "MSFT", scores=[3.0, 1.0])
        signals = evaluator.evaluate(result)
        assert len(signals) == 2
        assert signals[0].signal_type is SignalType.BUY
        assert signals[1].signal_type is SignalType.HOLD

    def test_with_max_rank(self) -> None:
        strat = Strategy([RSRankRule(top_n=1)])
        evaluator = StrategyEvaluator(strat, max_rank=1)
        result = _result("AAPL", "MSFT", scores=[3.0, 1.0])
        signals = evaluator.evaluate(result)
        assert len(signals) == 1
        assert signals[0].symbol.raw == "AAPL"

    def test_max_rank_filters_before_eval(self) -> None:
        strat = Strategy([RSValueRule(min_rs=0.5)])
        evaluator = StrategyEvaluator(strat, max_rank=2)
        result = _result("A", "B", "C", scores=[3.0, 2.0, 1.0])
        signals = evaluator.evaluate(result)
        assert len(signals) == 2

    def test_empty_result(self) -> None:
        strat = Strategy([_AlwaysBuy()])
        evaluator = StrategyEvaluator(strat)
        result = ScanResult(ranking=RankingResult())
        signals = evaluator.evaluate(result)
        assert len(signals) == 0

    def test_max_rank_validation(self) -> None:
        strat = Strategy([_AlwaysBuy()])
        with pytest.raises(ValueError, match="max_rank must be >= 1"):
            StrategyEvaluator(strat, max_rank=0)

    def test_properties(self) -> None:
        strat = Strategy([_AlwaysBuy()])
        evaluator = StrategyEvaluator(strat, max_rank=5)
        assert evaluator.strategy is strat
        assert evaluator.max_rank == 5
