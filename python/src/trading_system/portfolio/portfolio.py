"""Portfolio state tracker."""

from __future__ import annotations

from dataclasses import dataclass, field

from trading_system.models.symbol import Symbol
from trading_system.portfolio.position import Position, Side
from trading_system.portfolio.risk import RiskManager


@dataclass
class Portfolio:
    """Tracks positions, cash, equity, and drawdown."""

    cash: float
    positions: dict[Symbol, Position] = field(default_factory=dict)
    peak_equity: float = 0.0
    risk: RiskManager = field(default_factory=RiskManager)

    def __post_init__(self) -> None:
        if self.cash < 0:
            msg = f"cash must be non-negative, got {self.cash}"
            raise ValueError(msg)
        if self.peak_equity == 0:
            self.peak_equity = self.cash

    @property
    def total_exposure(self) -> float:
        """Total dollar value of all open positions."""
        return sum(p.market_value for p in self.positions.values())

    @property
    def total_equity(self) -> float:
        """Cash + market value of all positions."""
        return self.cash + self.total_exposure

    @property
    def drawdown(self) -> float:
        """Current drawdown from peak equity."""
        if self.peak_equity <= 0:
            return 0.0
        return (self.peak_equity - self.total_equity) / self.peak_equity

    @property
    def unrealized_pnl(self) -> float:
        """Total unrealized P&L across all positions."""
        return sum(p.unrealized_pnl for p in self.positions.values())

    def add_position(
        self,
        symbol: Symbol,
        side: Side,
        quantity: int,
        price: float,
    ) -> None:
        """Open or add to a position, deducting cash."""
        if symbol in self.positions:
            msg = f"position already exists for {symbol}"
            raise ValueError(msg)

        cost = quantity * price
        if cost > self.cash:
            msg = f"insufficient cash: need {cost}, have {self.cash}"
            raise ValueError(msg)

        pos = Position(
            symbol=symbol,
            side=side,
            quantity=quantity,
            entry_price=price,
            current_price=price,
        )
        self.positions[symbol] = pos
        self.cash -= cost
        self._update_peak()

    def remove_position(self, symbol: Symbol, price: float | None = None) -> float:
        """Close a position at the given price, returning realized P&L.

        If price is None, uses the position's current_price.
        """
        if symbol not in self.positions:
            msg = f"no position for {symbol}"
            raise KeyError(msg)

        pos = self.positions.pop(symbol)
        close_price = price if price is not None else pos.current_price
        realized = pos.side * pos.quantity * (close_price - pos.entry_price)
        self.cash += pos.quantity * close_price
        self._update_peak()
        return realized

    def update_prices(self, prices: dict[Symbol, float]) -> None:
        """Update current prices for held positions."""
        for sym, price in prices.items():
            if sym in self.positions:
                self.positions[sym] = self.positions[sym].update_price(price)
        self._update_peak()

    def position_value(self, symbol: Symbol) -> float:
        """Market value of a single position, or 0.0."""
        if symbol not in self.positions:
            return 0.0
        return self.positions[symbol].market_value

    def _update_peak(self) -> None:
        eq = self.total_equity
        if eq > self.peak_equity:
            self.peak_equity = eq
