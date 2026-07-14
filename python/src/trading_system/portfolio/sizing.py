"""Position sizing framework."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class SizingMethod(StrEnum):
    """Method used to determine position size."""

    FIXED_FRACTION = "FIXED_FRACTION"
    FIXED_DOLLAR = "FIXED_DOLLAR"


@dataclass(frozen=True, slots=True)
class SizingResult:
    """Output of a position sizing calculation."""

    method: SizingMethod
    quantity: int
    risk_per_share: float
    risk_budget: float
    position_size_dollars: float


class PositionSizer:
    """Calculates position size based on account equity and risk."""

    def __init__(
        self,
        method: SizingMethod = SizingMethod.FIXED_FRACTION,
        risk_pct: float = 0.02,
        fixed_dollar: float = 0.0,
    ) -> None:
        if risk_pct <= 0 or risk_pct > 1:
            msg = f"risk_pct must be in (0, 1], got {risk_pct}"
            raise ValueError(msg)
        self.method = method
        self.risk_pct = risk_pct
        self.fixed_dollar = fixed_dollar

    def size(
        self,
        equity: float,
        entry_price: float,
        stop_price: float,
    ) -> SizingResult:
        """Calculate position size.

        Parameters
        ----------
        equity:
            Total portfolio equity available.
        entry_price:
            Planned entry price.
        stop_price:
            Planned stop-loss price.
        """
        if equity <= 0:
            msg = f"equity must be positive, got {equity}"
            raise ValueError(msg)
        if entry_price <= 0:
            msg = f"entry_price must be positive, got {entry_price}"
            raise ValueError(msg)
        if stop_price <= 0:
            msg = f"stop_price must be positive, got {stop_price}"
            raise ValueError(msg)
        if entry_price == stop_price:
            msg = "entry_price and stop_price must differ"
            raise ValueError(msg)

        risk_per_share = abs(entry_price - stop_price)
        risk_budget = equity * self.risk_pct

        if self.method == SizingMethod.FIXED_FRACTION:
            quantity = max(1, int(risk_budget / risk_per_share))
            position_dollars = quantity * entry_price
        else:
            quantity = max(1, int(self.fixed_dollar / entry_price))
            position_dollars = quantity * entry_price

        return SizingResult(
            method=self.method,
            quantity=quantity,
            risk_per_share=risk_per_share,
            risk_budget=risk_budget,
            position_size_dollars=position_dollars,
        )
