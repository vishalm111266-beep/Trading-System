"""Tests for trading_system.portfolio.position."""

import pytest
from trading_system.models.symbol import Symbol
from trading_system.portfolio.position import Position, Side


class TestSide:
    def test_long_is_positive(self) -> None:
        assert Side.LONG == 1

    def test_short_is_negative(self) -> None:
        assert Side.SHORT == -1


class TestPositionInit:
    def test_long_position(self) -> None:
        pos = Position(
            symbol=Symbol(raw="AAPL"),
            side=Side.LONG,
            quantity=100,
            entry_price=150.0,
            current_price=155.0,
        )
        assert pos.symbol.raw == "AAPL"
        assert pos.side == Side.LONG
        assert pos.quantity == 100
        assert pos.entry_price == 150.0
        assert pos.current_price == 155.0

    def test_short_position(self) -> None:
        pos = Position(
            symbol=Symbol(raw="TSLA"),
            side=Side.SHORT,
            quantity=50,
            entry_price=200.0,
            current_price=190.0,
        )
        assert pos.side == Side.SHORT

    def test_invalid_quantity(self) -> None:
        with pytest.raises(ValueError, match="quantity must be positive"):
            Position(
                symbol=Symbol(raw="X"),
                side=Side.LONG,
                quantity=0,
                entry_price=10.0,
                current_price=10.0,
            )

    def test_invalid_entry_price(self) -> None:
        with pytest.raises(ValueError, match="entry_price must be positive"):
            Position(
                symbol=Symbol(raw="X"),
                side=Side.LONG,
                quantity=10,
                entry_price=0.0,
                current_price=10.0,
            )

    def test_invalid_current_price(self) -> None:
        with pytest.raises(ValueError, match="current_price must be positive"):
            Position(
                symbol=Symbol(raw="X"),
                side=Side.LONG,
                quantity=10,
                entry_price=10.0,
                current_price=-1.0,
            )


class TestPositionProperties:
    def test_market_value_long(self) -> None:
        pos = Position(
            symbol=Symbol(raw="AAPL"),
            side=Side.LONG,
            quantity=100,
            entry_price=150.0,
            current_price=160.0,
        )
        assert pos.market_value == 16000.0

    def test_cost_basis(self) -> None:
        pos = Position(
            symbol=Symbol(raw="AAPL"),
            side=Side.LONG,
            quantity=100,
            entry_price=150.0,
            current_price=160.0,
        )
        assert pos.cost_basis == 15000.0

    def test_unrealized_pnl_long_profit(self) -> None:
        pos = Position(
            symbol=Symbol(raw="AAPL"),
            side=Side.LONG,
            quantity=100,
            entry_price=150.0,
            current_price=160.0,
        )
        assert pos.unrealized_pnl == 1000.0

    def test_unrealized_pnl_long_loss(self) -> None:
        pos = Position(
            symbol=Symbol(raw="AAPL"),
            side=Side.LONG,
            quantity=100,
            entry_price=150.0,
            current_price=140.0,
        )
        assert pos.unrealized_pnl == -1000.0

    def test_unrealized_pnl_short_profit(self) -> None:
        pos = Position(
            symbol=Symbol(raw="TSLA"),
            side=Side.SHORT,
            quantity=50,
            entry_price=200.0,
            current_price=180.0,
        )
        assert pos.unrealized_pnl == 1000.0

    def test_unrealized_pnl_short_loss(self) -> None:
        pos = Position(
            symbol=Symbol(raw="TSLA"),
            side=Side.SHORT,
            quantity=50,
            entry_price=200.0,
            current_price=220.0,
        )
        assert pos.unrealized_pnl == -1000.0


class TestPositionUpdatePrice:
    def test_returns_new_position(self) -> None:
        pos = Position(
            symbol=Symbol(raw="AAPL"),
            side=Side.LONG,
            quantity=100,
            entry_price=150.0,
            current_price=155.0,
        )
        updated = pos.update_price(160.0)
        assert updated.current_price == 160.0
        assert pos.current_price == 155.0  # original unchanged

    def test_invalid_price(self) -> None:
        pos = Position(
            symbol=Symbol(raw="AAPL"),
            side=Side.LONG,
            quantity=100,
            entry_price=150.0,
            current_price=155.0,
        )
        with pytest.raises(ValueError, match="price must be positive"):
            pos.update_price(0.0)
