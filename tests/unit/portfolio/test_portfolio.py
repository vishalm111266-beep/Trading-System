"""Tests for trading_system.portfolio.portfolio."""

import pytest
from trading_system.models.symbol import Symbol
from trading_system.portfolio.portfolio import Portfolio
from trading_system.portfolio.position import Side


class TestPortfolioInit:
    def test_defaults(self) -> None:
        p = Portfolio(cash=100000)
        assert p.cash == 100000
        assert p.positions == {}
        assert p.peak_equity == 100000

    def test_negative_cash(self) -> None:
        with pytest.raises(ValueError, match="cash must be non-negative"):
            Portfolio(cash=-1)


class TestPortfolioEquity:
    def test_empty(self) -> None:
        p = Portfolio(cash=100000)
        assert p.total_equity == 100000
        assert p.total_exposure == 0

    def test_with_positions(self) -> None:
        p = Portfolio(cash=100000)
        sym = Symbol(raw="AAPL")
        p.add_position(sym, Side.LONG, 100, 150.0)
        assert p.total_exposure == pytest.approx(15000)
        assert p.total_equity == pytest.approx(100000 - 15000 + 15000)

    def test_drawdown(self) -> None:
        p = Portfolio(cash=100000)
        sym = Symbol(raw="AAPL")
        p.add_position(sym, Side.LONG, 100, 150.0)
        p.update_prices({sym: 100.0})
        assert p.drawdown == pytest.approx((100000 - (100000 - 15000 + 10000)) / 100000)

    def test_unrealized_pnl(self) -> None:
        p = Portfolio(cash=100000)
        sym = Symbol(raw="AAPL")
        p.add_position(sym, Side.LONG, 100, 150.0)
        p.update_prices({sym: 160.0})
        assert p.unrealized_pnl == pytest.approx(1000.0)


class TestPortfolioAddPosition:
    def test_adds_position(self) -> None:
        p = Portfolio(cash=100000)
        sym = Symbol(raw="AAPL")
        p.add_position(sym, Side.LONG, 100, 150.0)
        assert sym in p.positions
        assert p.cash == pytest.approx(85000)

    def test_deducts_cash(self) -> None:
        p = Portfolio(cash=100000)
        sym = Symbol(raw="AAPL")
        p.add_position(sym, Side.LONG, 100, 150.0)
        assert p.cash == pytest.approx(85000)

    def test_duplicate_position_raises(self) -> None:
        p = Portfolio(cash=100000)
        sym = Symbol(raw="AAPL")
        p.add_position(sym, Side.LONG, 100, 150.0)
        with pytest.raises(ValueError, match="position already exists"):
            p.add_position(sym, Side.LONG, 50, 155.0)

    def test_insufficient_cash(self) -> None:
        p = Portfolio(cash=10000)
        sym = Symbol(raw="AAPL")
        with pytest.raises(ValueError, match="insufficient cash"):
            p.add_position(sym, Side.LONG, 100, 150.0)

    def test_short_position(self) -> None:
        p = Portfolio(cash=100000)
        sym = Symbol(raw="TSLA")
        p.add_position(sym, Side.SHORT, 50, 200.0)
        assert p.positions[sym].side == Side.SHORT
        assert p.cash == pytest.approx(90000)


class TestPortfolioRemovePosition:
    def test_removes_position(self) -> None:
        p = Portfolio(cash=100000)
        sym = Symbol(raw="AAPL")
        p.add_position(sym, Side.LONG, 100, 150.0)
        realized = p.remove_position(sym, 160.0)
        assert sym not in p.positions
        assert realized == pytest.approx(1000.0)

    def test_returns_realized_pnl(self) -> None:
        p = Portfolio(cash=100000)
        sym = Symbol(raw="AAPL")
        p.add_position(sym, Side.LONG, 100, 150.0)
        realized = p.remove_position(sym, 140.0)
        assert realized == pytest.approx(-1000.0)

    def test_restores_cash(self) -> None:
        p = Portfolio(cash=100000)
        sym = Symbol(raw="AAPL")
        p.add_position(sym, Side.LONG, 100, 150.0)
        cash_before = p.cash
        p.remove_position(sym, 160.0)
        assert p.cash == pytest.approx(cash_before + 16000)

    def test_no_position_raises(self) -> None:
        p = Portfolio(cash=100000)
        with pytest.raises(KeyError, match="no position"):
            p.remove_position(Symbol(raw="AAPL"))

    def test_uses_current_price_if_no_price(self) -> None:
        p = Portfolio(cash=100000)
        sym = Symbol(raw="AAPL")
        p.add_position(sym, Side.LONG, 100, 150.0)
        p.update_prices({sym: 155.0})
        realized = p.remove_position(sym)
        assert realized == pytest.approx(500.0)


class TestPortfolioUpdatePrices:
    def test_updates_prices(self) -> None:
        p = Portfolio(cash=100000)
        sym = Symbol(raw="AAPL")
        p.add_position(sym, Side.LONG, 100, 150.0)
        p.update_prices({sym: 160.0})
        assert p.positions[sym].current_price == 160.0

    def test_updates_peak_equity(self) -> None:
        p = Portfolio(cash=100000)
        sym = Symbol(raw="AAPL")
        p.add_position(sym, Side.LONG, 100, 150.0)
        p.update_prices({sym: 200.0})
        assert p.peak_equity == pytest.approx(105000)

    def test_unknown_symbol_ignored(self) -> None:
        p = Portfolio(cash=100000)
        sym = Symbol(raw="AAPL")
        p.add_position(sym, Side.LONG, 100, 150.0)
        p.update_prices({Symbol(raw="MSFT"): 300.0})
        assert p.positions[sym].current_price == 150.0


class TestPortfolioPositionValue:
    def test_existing_position(self) -> None:
        p = Portfolio(cash=100000)
        sym = Symbol(raw="AAPL")
        p.add_position(sym, Side.LONG, 100, 150.0)
        assert p.position_value(sym) == pytest.approx(15000)

    def test_missing_position(self) -> None:
        p = Portfolio(cash=100000)
        assert p.position_value(Symbol(raw="AAPL")) == 0.0


class TestPortfolioDrawdown:
    def test_no_drawdown_initially(self) -> None:
        p = Portfolio(cash=100000)
        assert p.drawdown == 0.0

    def test_drawdown_after_loss(self) -> None:
        p = Portfolio(cash=100000)
        sym = Symbol(raw="AAPL")
        p.add_position(sym, Side.LONG, 100, 150.0)
        p.update_prices({sym: 50.0})
        assert p.drawdown > 0

    def test_peak_resets_higher(self) -> None:
        p = Portfolio(cash=100000)
        sym = Symbol(raw="AAPL")
        p.add_position(sym, Side.LONG, 100, 150.0)
        p.update_prices({sym: 200.0})
        assert p.peak_equity == pytest.approx(105000)
        p.update_prices({sym: 100.0})
        assert p.peak_equity == pytest.approx(105000)
