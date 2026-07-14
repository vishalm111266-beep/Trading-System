"""Base strategy rule interface and rule composition."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from trading_system.models.symbol import Symbol
from trading_system.scanner.result import ScanDetail, ScanResult
from trading_system.strategies.signal import Signal, SignalType


class StrategyRule(ABC):
    """Interface for a single evaluation rule."""

    @abstractmethod
    def evaluate(self, detail: ScanDetail, result: ScanResult) -> tuple[SignalType, str]:
        """Evaluate a stock and return ``(signal_type, reason)``."""


class Strategy:
    """Composes multiple rules and evaluates them per stock.

    Rules are evaluated in order. The first non-HOLD signal wins.
    If all rules return HOLD, the final signal is HOLD.
    """

    def __init__(self, rules: Sequence[StrategyRule]) -> None:
        if not rules:
            msg = "strategy must have at least one rule"
            raise ValueError(msg)
        self._rules = list(rules)

    @property
    def rules(self) -> list[StrategyRule]:
        return list(self._rules)

    def evaluate(self, result: ScanResult) -> tuple[Signal, ...]:
        """Evaluate every ranked stock in *result*."""
        signals: list[Signal] = []
        for entry in result.ranking.entries:
            detail = _find_detail(result, entry.symbol)
            if detail is None:
                signals.append(
                    Signal(
                        symbol=entry.symbol,
                        signal_type=SignalType.IGNORE,
                        reason="no scan detail available",
                        rank=entry.rank,
                        score=entry.score,
                    )
                )
                continue
            signal_type, reason = self._evaluate_rules(detail, result)
            signals.append(
                Signal(
                    symbol=entry.symbol,
                    signal_type=signal_type,
                    reason=reason,
                    rank=entry.rank,
                    score=entry.score,
                )
            )
        return tuple(signals)

    def _evaluate_rules(self, detail: ScanDetail, result: ScanResult) -> tuple[SignalType, str]:
        for rule in self._rules:
            signal_type, reason = rule.evaluate(detail, result)
            if signal_type != SignalType.HOLD:
                return signal_type, reason
        return SignalType.HOLD, "all rules returned HOLD"


def _find_detail(result: ScanResult, symbol: Symbol) -> ScanDetail | None:
    for detail in result.details:
        if detail.symbol == symbol:
            return detail
    return None
