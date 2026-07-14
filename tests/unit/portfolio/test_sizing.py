"""Tests for trading_system.portfolio.sizing."""

import pytest
from trading_system.portfolio.sizing import PositionSizer, SizingMethod


class TestPositionSizerInit:
    def test_defaults(self) -> None:
        sizer = PositionSizer()
        assert sizer.method == SizingMethod.FIXED_FRACTION
        assert sizer.risk_pct == 0.02

    def test_custom_fraction(self) -> None:
        sizer = PositionSizer(method=SizingMethod.FIXED_FRACTION, risk_pct=0.05)
        assert sizer.risk_pct == 0.05

    def test_fixed_dollar(self) -> None:
        sizer = PositionSizer(method=SizingMethod.FIXED_DOLLAR, fixed_dollar=5000)
        assert sizer.fixed_dollar == 5000

    def test_invalid_risk_pct_zero(self) -> None:
        with pytest.raises(ValueError, match="risk_pct must be in"):
            PositionSizer(risk_pct=0.0)

    def test_invalid_risk_pct_one(self) -> None:
        with pytest.raises(ValueError, match="risk_pct must be in"):
            PositionSizer(risk_pct=1.1)

    def test_negative_risk_pct(self) -> None:
        with pytest.raises(ValueError, match="risk_pct must be in"):
            PositionSizer(risk_pct=-0.01)


class TestPositionSizerFixedFraction:
    def test_basic(self) -> None:
        sizer = PositionSizer(method=SizingMethod.FIXED_FRACTION, risk_pct=0.02)
        result = sizer.size(equity=100000, entry_price=150.0, stop_price=145.0)
        assert result.method == SizingMethod.FIXED_FRACTION
        assert result.risk_per_share == 5.0
        assert result.risk_budget == 2000.0
        assert result.quantity == 400
        assert result.position_size_dollars == 60000.0

    def test_minimum_quantity_one(self) -> None:
        sizer = PositionSizer(method=SizingMethod.FIXED_FRACTION, risk_pct=0.01)
        result = sizer.size(equity=1000, entry_price=100.0, stop_price=50.0)
        assert result.quantity >= 1

    def test_stop_above_entry(self) -> None:
        sizer = PositionSizer(method=SizingMethod.FIXED_FRACTION, risk_pct=0.02)
        result = sizer.size(equity=100000, entry_price=100.0, stop_price=110.0)
        assert result.risk_per_share == 10.0
        assert result.quantity == 200


class TestPositionSizerFixedDollar:
    def test_basic(self) -> None:
        sizer = PositionSizer(method=SizingMethod.FIXED_DOLLAR, risk_pct=0.02, fixed_dollar=10000)
        result = sizer.size(equity=100000, entry_price=100.0, stop_price=90.0)
        assert result.method == SizingMethod.FIXED_DOLLAR
        assert result.quantity == 100
        assert result.position_size_dollars == 10000.0

    def test_minimum_quantity_one(self) -> None:
        sizer = PositionSizer(method=SizingMethod.FIXED_DOLLAR, risk_pct=0.02, fixed_dollar=50)
        result = sizer.size(equity=100000, entry_price=100.0, stop_price=90.0)
        assert result.quantity == 1


class TestPositionSizerValidation:
    def test_zero_equity(self) -> None:
        sizer = PositionSizer()
        with pytest.raises(ValueError, match="equity must be positive"):
            sizer.size(equity=0, entry_price=100.0, stop_price=90.0)

    def test_negative_entry_price(self) -> None:
        sizer = PositionSizer()
        with pytest.raises(ValueError, match="entry_price must be positive"):
            sizer.size(equity=100000, entry_price=-1.0, stop_price=90.0)

    def test_zero_stop_price(self) -> None:
        sizer = PositionSizer()
        with pytest.raises(ValueError, match="stop_price must be positive"):
            sizer.size(equity=100000, entry_price=100.0, stop_price=0.0)

    def test_equal_entry_and_stop(self) -> None:
        sizer = PositionSizer()
        with pytest.raises(ValueError, match="entry_price and stop_price must differ"):
            sizer.size(equity=100000, entry_price=100.0, stop_price=100.0)
