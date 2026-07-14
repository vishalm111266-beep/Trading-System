"""Concrete strategy rules for RS-based evaluation."""

from __future__ import annotations

from trading_system.scanner.result import ScanDetail, ScanResult
from trading_system.strategies.base import StrategyRule
from trading_system.strategies.signal import SignalType


class RSRankRule(StrategyRule):
    """Signal based on a stock's rank position."""

    def __init__(self, top_n: int, *, signal: SignalType = SignalType.BUY) -> None:
        if top_n < 1:
            msg = f"top_n must be >= 1, got {top_n}"
            raise ValueError(msg)
        self._top_n = top_n
        self._signal = signal

    def evaluate(self, detail: ScanDetail, result: ScanResult) -> tuple[SignalType, str]:
        for entry in result.ranking.entries:
            if entry.symbol == detail.symbol:
                if entry.rank <= self._top_n:
                    return self._signal, f"rank {entry.rank} <= top_n {self._top_n}"
                return SignalType.HOLD, f"rank {entry.rank} > top_n {self._top_n}"
        return SignalType.HOLD, "symbol not in ranking"


class RSValueRule(StrategyRule):
    """Signal based on a minimum RS value threshold."""

    def __init__(self, min_rs: float, *, signal: SignalType = SignalType.BUY) -> None:
        self._min_rs = min_rs
        self._signal = signal

    def evaluate(self, detail: ScanDetail, result: ScanResult) -> tuple[SignalType, str]:
        if detail.rs_value >= self._min_rs:
            return self._signal, f"rs_value {detail.rs_value} >= min_rs {self._min_rs}"
        return SignalType.HOLD, f"rs_value {detail.rs_value} < min_rs {self._min_rs}"


class MansfieldRSRule(StrategyRule):
    """Signal based on Mansfield RS positive / negative."""

    def __init__(
        self,
        *,
        positive_signal: SignalType = SignalType.BUY,
        negative_signal: SignalType = SignalType.SELL,
    ) -> None:
        self._positive_signal = positive_signal
        self._negative_signal = negative_signal

    def evaluate(self, detail: ScanDetail, result: ScanResult) -> tuple[SignalType, str]:
        if detail.mansfield_rs is None:
            return SignalType.HOLD, "mansfield_rs is None"
        if detail.mansfield_rs > 0:
            return self._positive_signal, f"mansfield_rs {detail.mansfield_rs} > 0"
        if detail.mansfield_rs < 0:
            return self._negative_signal, f"mansfield_rs {detail.mansfield_rs} < 0"
        return SignalType.HOLD, f"mansfield_rs {detail.mansfield_rs} == 0"


class ReturnRule(StrategyRule):
    """Signal based on stock return thresholds."""

    def __init__(
        self,
        min_return: float = 0.0,
        max_return: float = 0.0,
        *,
        buy_signal: SignalType = SignalType.BUY,
        sell_signal: SignalType = SignalType.SELL,
    ) -> None:
        self._min_return = min_return
        self._max_return = max_return
        self._buy_signal = buy_signal
        self._sell_signal = sell_signal

    def evaluate(self, detail: ScanDetail, result: ScanResult) -> tuple[SignalType, str]:
        ret = detail.stock_return
        if ret >= self._min_return:
            return self._buy_signal, f"stock_return {ret} >= min_return {self._min_return}"
        if ret <= self._max_return:
            return self._sell_signal, f"stock_return {ret} <= max_return {self._max_return}"
        return SignalType.HOLD, f"stock_return {ret} in neutral zone"
