"""Risk management framework."""

from __future__ import annotations

from dataclasses import dataclass

from trading_system.portfolio.position import Position


@dataclass(frozen=True, slots=True)
class RiskLimits:
    """Portfolio-level risk constraints."""

    max_position_pct: float = 0.20
    max_total_exposure_pct: float = 1.00
    max_drawdown_pct: float = 0.25

    def __post_init__(self) -> None:
        if self.max_position_pct <= 0 or self.max_position_pct > 1:
            msg = f"max_position_pct must be in (0, 1], got {self.max_position_pct}"
            raise ValueError(msg)
        if self.max_total_exposure_pct <= 0 or self.max_total_exposure_pct > 2:
            msg = f"max_total_exposure_pct must be in (0, 2], got {self.max_total_exposure_pct}"
            raise ValueError(msg)
        if self.max_drawdown_pct <= 0 or self.max_drawdown_pct > 1:
            msg = f"max_drawdown_pct must be in (0, 1], got {self.max_drawdown_pct}"
            raise ValueError(msg)


class RiskManager:
    """Enforces portfolio risk limits."""

    def __init__(self, limits: RiskLimits | None = None) -> None:
        self.limits = limits or RiskLimits()

    def check_position_size(
        self,
        dollar_amount: float,
        equity: float,
    ) -> bool:
        """Return True if the position size is within the limit."""
        if equity <= 0:
            return False
        pct = dollar_amount / equity
        return pct <= self.limits.max_position_pct

    def check_total_exposure(
        self,
        positions: dict[object, Position],
        new_dollar: float,
        equity: float,
    ) -> bool:
        """Return True if adding new_dollar keeps total exposure within limit."""
        if equity <= 0:
            return False
        current = sum(p.market_value for p in positions.values())
        total = current + new_dollar
        return total / equity <= self.limits.max_total_exposure_pct

    def clamp_position_size(
        self,
        dollar_amount: float,
        equity: float,
    ) -> float:
        """Clamp position dollar amount to max_position_pct of equity."""
        if equity <= 0:
            return 0.0
        max_dollars = equity * self.limits.max_position_pct
        return min(dollar_amount, max_dollars)

    def check_drawdown(
        self,
        current_equity: float,
        peak_equity: float,
    ) -> bool:
        """Return True if drawdown is within the limit."""
        if peak_equity <= 0:
            return False
        drawdown = (peak_equity - current_equity) / peak_equity
        return drawdown <= self.limits.max_drawdown_pct

    def filter_by_risk(
        self,
        positions: dict[object, Position],
        equity: float,
    ) -> dict[object, Position]:
        """Return a subset of positions that respect risk limits."""
        if equity <= 0:
            return {}
        result: dict[object, Position] = {}
        total_exposure = 0.0
        max_exposure = equity * self.limits.max_total_exposure_pct
        max_single = equity * self.limits.max_position_pct

        for key, pos in positions.items():
            mv = pos.market_value
            if mv > max_single:
                continue
            if total_exposure + mv > max_exposure:
                continue
            result[key] = pos
            total_exposure += mv

        return result
