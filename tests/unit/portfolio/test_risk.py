"""Tests for trading_system.portfolio.risk."""

import pytest
from trading_system.models.symbol import Symbol
from trading_system.portfolio.position import Position, Side
from trading_system.portfolio.risk import RiskLimits, RiskManager


class TestRiskLimits:
    def test_defaults(self) -> None:
        limits = RiskLimits()
        assert limits.max_position_pct == 0.20
        assert limits.max_total_exposure_pct == 1.00
        assert limits.max_drawdown_pct == 0.25

    def test_custom(self) -> None:
        limits = RiskLimits(max_position_pct=0.10, max_drawdown_pct=0.15)
        assert limits.max_position_pct == 0.10
        assert limits.max_drawdown_pct == 0.15

    def test_invalid_position_pct(self) -> None:
        with pytest.raises(ValueError, match="max_position_pct must be in"):
            RiskLimits(max_position_pct=0.0)

    def test_invalid_position_pct_over_one(self) -> None:
        with pytest.raises(ValueError, match="max_position_pct must be in"):
            RiskLimits(max_position_pct=1.5)

    def test_invalid_exposure_pct(self) -> None:
        with pytest.raises(ValueError, match="max_total_exposure_pct must be in"):
            RiskLimits(max_total_exposure_pct=0.0)

    def test_invalid_drawdown_pct(self) -> None:
        with pytest.raises(ValueError, match="max_drawdown_pct must be in"):
            RiskLimits(max_drawdown_pct=0.0)


def _pos(symbol: str, qty: int, price: float, side: Side = Side.LONG) -> Position:
    return Position(
        symbol=Symbol(raw=symbol),
        side=side,
        quantity=qty,
        entry_price=price,
        current_price=price,
    )


class TestRiskManagerCheckPositionSize:
    def test_within_limit(self) -> None:
        rm = RiskManager(RiskLimits(max_position_pct=0.20))
        assert rm.check_position_size(dollar_amount=15000, equity=100000) is True

    def test_at_limit(self) -> None:
        rm = RiskManager(RiskLimits(max_position_pct=0.20))
        assert rm.check_position_size(dollar_amount=20000, equity=100000) is True

    def test_over_limit(self) -> None:
        rm = RiskManager(RiskLimits(max_position_pct=0.20))
        assert rm.check_position_size(dollar_amount=25000, equity=100000) is False

    def test_zero_equity(self) -> None:
        rm = RiskManager()
        assert rm.check_position_size(dollar_amount=100, equity=0) is False


class TestRiskManagerCheckTotalExposure:
    def test_within_limit(self) -> None:
        rm = RiskManager(RiskLimits(max_total_exposure_pct=1.0))
        positions = {"A": _pos("A", 100, 100.0)}
        assert rm.check_total_exposure(positions, new_dollar=5000, equity=100000) is True

    def test_over_limit(self) -> None:
        rm = RiskManager(RiskLimits(max_total_exposure_pct=0.50))
        positions = {"A": _pos("A", 400, 100.0)}
        assert rm.check_total_exposure(positions, new_dollar=20000, equity=100000) is False

    def test_zero_equity(self) -> None:
        rm = RiskManager()
        assert rm.check_total_exposure({}, new_dollar=100, equity=0) is False


class TestRiskManagerClampPositionSize:
    def test_within_limit(self) -> None:
        rm = RiskManager(RiskLimits(max_position_pct=0.20))
        assert rm.clamp_position_size(15000, 100000) == 15000

    def test_clamped(self) -> None:
        rm = RiskManager(RiskLimits(max_position_pct=0.20))
        assert rm.clamp_position_size(30000, 100000) == 20000

    def test_zero_equity(self) -> None:
        rm = RiskManager()
        assert rm.clamp_position_size(10000, 0) == 0.0


class TestRiskManagerCheckDrawdown:
    def test_within_limit(self) -> None:
        rm = RiskManager(RiskLimits(max_drawdown_pct=0.25))
        assert rm.check_drawdown(current_equity=80000, peak_equity=100000) is True

    def test_at_limit(self) -> None:
        rm = RiskManager(RiskLimits(max_drawdown_pct=0.25))
        assert rm.check_drawdown(current_equity=75000, peak_equity=100000) is True

    def test_over_limit(self) -> None:
        rm = RiskManager(RiskLimits(max_drawdown_pct=0.25))
        assert rm.check_drawdown(current_equity=70000, peak_equity=100000) is False

    def test_zero_peak(self) -> None:
        rm = RiskManager()
        assert rm.check_drawdown(current_equity=100000, peak_equity=0) is False


class TestRiskManagerFilterByRisk:
    def test_filters_single_too_large(self) -> None:
        rm = RiskManager(RiskLimits(max_position_pct=0.20))
        positions = {
            "A": _pos("A", 100, 100.0),  # 10000 — ok
            "B": _pos("B", 300, 100.0),  # 30000 — too large
        }
        result = rm.filter_by_risk(positions, equity=100000)
        assert "A" in result
        assert "B" not in result

    def test_filters_exceeding_total_exposure(self) -> None:
        rm = RiskManager(RiskLimits(max_total_exposure_pct=0.50))
        positions = {
            "A": _pos("A", 200, 100.0),  # 20000
            "B": _pos("B", 200, 100.0),  # 20000
            "C": _pos("C", 200, 100.0),  # 20000 — total 60000 > 50000
        }
        result = rm.filter_by_risk(positions, equity=100000)
        assert len(result) == 2

    def test_empty_positions(self) -> None:
        rm = RiskManager()
        assert rm.filter_by_risk({}, equity=100000) == {}

    def test_zero_equity(self) -> None:
        rm = RiskManager()
        positions = {"A": _pos("A", 100, 100.0)}
        assert rm.filter_by_risk(positions, equity=0) == {}
