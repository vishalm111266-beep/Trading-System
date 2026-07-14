"""Tests for trading_system.strategies.signal."""

from trading_system.models.symbol import Symbol
from trading_system.strategies.signal import Signal, SignalType


class TestSignalType:
    def test_values(self) -> None:
        assert SignalType.BUY == "BUY"
        assert SignalType.HOLD == "HOLD"
        assert SignalType.SELL == "SELL"
        assert SignalType.IGNORE == "IGNORE"

    def test_is_str_enum(self) -> None:
        assert isinstance(SignalType.BUY, str)
        assert SignalType("BUY") is SignalType.BUY


class TestSignal:
    def test_creation(self) -> None:
        sig = Signal(
            symbol=Symbol(raw="AAPL"),
            signal_type=SignalType.BUY,
            reason="rank 1 <= top_n 5",
            rank=1,
            score=2.5,
        )
        assert sig.symbol.raw == "AAPL"
        assert sig.signal_type is SignalType.BUY
        assert sig.reason == "rank 1 <= top_n 5"
        assert sig.rank == 1
        assert sig.score == 2.5

    def test_defaults(self) -> None:
        sig = Signal(
            symbol=Symbol(raw="X"),
            signal_type=SignalType.HOLD,
            reason="ok",
        )
        assert sig.rank == 0
        assert sig.score == 0.0

    def test_frozen(self) -> None:
        sig = Signal(
            symbol=Symbol(raw="X"),
            signal_type=SignalType.SELL,
            reason="test",
        )
        import pytest

        with pytest.raises(AttributeError):
            sig.signal_type = SignalType.BUY  # type: ignore[misc]
