"""Position and side models."""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

from trading_system.models.symbol import Symbol


class Side(IntEnum):
    """Position direction."""

    LONG = 1
    SHORT = -1


@dataclass(frozen=True, slots=True)
class Position:
    """A single position in a symbol."""

    symbol: Symbol
    side: Side
    quantity: int
    entry_price: float
    current_price: float

    def __post_init__(self) -> None:
        if self.quantity <= 0:
            msg = f"quantity must be positive, got {self.quantity}"
            raise ValueError(msg)
        if self.entry_price <= 0:
            msg = f"entry_price must be positive, got {self.entry_price}"
            raise ValueError(msg)
        if self.current_price <= 0:
            msg = f"current_price must be positive, got {self.current_price}"
            raise ValueError(msg)

    @property
    def market_value(self) -> float:
        """Current market value of the position."""
        return self.quantity * self.current_price

    @property
    def cost_basis(self) -> float:
        """Original cost basis of the position."""
        return self.quantity * self.entry_price

    @property
    def unrealized_pnl(self) -> float:
        """Unrealized profit/loss."""
        return self.side * self.quantity * (self.current_price - self.entry_price)

    def update_price(self, price: float) -> Position:
        """Return a new Position with updated current_price."""
        if price <= 0:
            msg = f"price must be positive, got {price}"
            raise ValueError(msg)
        return Position(
            symbol=self.symbol,
            side=self.side,
            quantity=self.quantity,
            entry_price=self.entry_price,
            current_price=price,
        )
