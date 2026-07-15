"""Risk analysis tools for portfolio and position risk assessment."""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from trading_system.portfolio.portfolio import Portfolio


@dataclass(frozen=True, slots=True)
class RiskReport:
    """Comprehensive risk analysis report."""

    portfolio_var_95: float
    portfolio_var_99: float
    portfolio_volatility: float
    position_concentration: float
    max_position_pct: float
    correlation_risk: float
    tail_risk: float
    kelly_fraction: float
    risk_score: str
    warnings: list[str] = field(default_factory=list)


class RiskAnalyzer:
    """Analyze portfolio and position risk metrics.

    Usage::

        analyzer = RiskAnalyzer()
        report = analyzer.analyze_portfolio(portfolio)
        var = analyzer.calculate_var(prices, confidence=0.95)
    """

    def analyze_portfolio(self, portfolio: Portfolio) -> RiskReport:
        """Generate a comprehensive risk report for the portfolio."""
        warnings: list[str] = []

        equity = portfolio.total_equity
        if equity <= 0:
            return self._empty_report(["portfolio has zero or negative equity"])

        position_values = {sym: pos.market_value for sym, pos in portfolio.positions.items()}
        total_exposure = sum(position_values.values())

        concentration = total_exposure / equity if equity > 0 else 0.0
        max_pos_pct = max((v / equity for v in position_values.values()), default=0.0)

        if concentration > 0.8:
            warnings.append(f"high total exposure: {concentration:.1%}")
        if max_pos_pct > 0.25:
            warnings.append(f"large single position: {max_pos_pct:.1%}")
        if portfolio.drawdown > 0.15:
            warnings.append(f"significant drawdown: {portfolio.drawdown:.1%}")

        var_95 = self._estimate_portfolio_var(portfolio, 0.95)
        var_99 = self._estimate_portfolio_var(portfolio, 0.99)
        volatility = self._estimate_portfolio_volatility(portfolio)

        kelly = self._calculate_kelly(portfolio)

        risk_score = self._calculate_risk_score(
            concentration, max_pos_pct, portfolio.drawdown, var_95
        )

        return RiskReport(
            portfolio_var_95=var_95,
            portfolio_var_99=var_99,
            portfolio_volatility=volatility,
            position_concentration=concentration,
            max_position_pct=max_pos_pct,
            correlation_risk=0.0,
            tail_risk=var_99 / var_95 if var_95 > 0 else 0.0,
            kelly_fraction=kelly,
            risk_score=risk_score,
            warnings=warnings,
        )

    def calculate_var(
        self,
        prices: list[float],
        confidence: float = 0.95,
        holding_period: int = 1,
    ) -> float:
        """Calculate Value at Risk using historical simulation.

        Args:
            prices: Historical price series.
            confidence: Confidence level (e.g., 0.95 for 95%).
            holding_period: Number of days for the VaR estimate.

        Returns:
            VaR as a percentage of portfolio value.
        """
        if len(prices) < 10:
            return 0.0

        returns = [(prices[i] - prices[i - 1]) / prices[i - 1] for i in range(1, len(prices))]
        returns.sort()

        index = int((1 - confidence) * len(returns))
        index = max(0, min(index, len(returns) - 1))

        var = abs(returns[index])
        return var * math.sqrt(holding_period)

    def calculate_cvar(
        self,
        prices: list[float],
        confidence: float = 0.95,
    ) -> float:
        """Calculate Conditional Value at Risk (Expected Shortfall)."""
        if len(prices) < 10:
            return 0.0

        returns = [(prices[i] - prices[i - 1]) / prices[i - 1] for i in range(1, len(prices))]
        returns.sort()

        cutoff = int((1 - confidence) * len(returns))
        cutoff = max(1, cutoff)

        tail_returns = returns[:cutoff]
        return abs(sum(tail_returns) / len(tail_returns)) if tail_returns else 0.0

    def calculate_position_sizing(
        self,
        equity: float,
        risk_per_trade_pct: float,
        entry_price: float,
        stop_loss_price: float,
    ) -> int:
        """Calculate position size based on risk per trade.

        Uses the formula: shares = (equity * risk_pct) / |entry - stop|

        Returns:
            Number of shares to buy.
        """
        if entry_price <= 0 or stop_loss_price <= 0:
            return 0
        if entry_price == stop_loss_price:
            return 0

        risk_amount = equity * risk_per_trade_pct
        risk_per_share = abs(entry_price - stop_loss_price)

        if risk_per_share <= 0:
            return 0

        shares = int(risk_amount / risk_per_share)
        return max(0, shares)

    def calculate_max_drawdown(self, equity_curve: list[float]) -> tuple[float, int, int]:
        """Calculate maximum drawdown and its start/end indices.

        Returns:
            Tuple of (max_drawdown_pct, peak_index, trough_index).
        """
        if len(equity_curve) < 2:
            return 0.0, 0, 0

        peak = equity_curve[0]
        peak_idx = 0
        max_dd = 0.0
        dd_peak_idx = 0
        dd_trough_idx = 0

        for i, eq in enumerate(equity_curve):
            if eq > peak:
                peak = eq
                peak_idx = i

            dd = (peak - eq) / peak if peak > 0 else 0.0
            if dd > max_dd:
                max_dd = dd
                dd_peak_idx = peak_idx
                dd_trough_idx = i

        return max_dd, dd_peak_idx, dd_trough_idx

    def stress_test(
        self,
        portfolio: Portfolio,
        shock_pct: float = -0.10,
    ) -> dict:
        """Apply a stress scenario to the portfolio.

        Args:
            portfolio: The portfolio to stress test.
            shock_pct: Market shock as a negative percentage (e.g., -0.10 for -10%).

        Returns:
            Dictionary with pre/post values and impact.
        """
        pre_equity = portfolio.total_equity
        pre_exposure = portfolio.total_exposure
        pre_positions = len(portfolio.positions)

        impact = pre_exposure * shock_pct
        post_equity = pre_equity + impact

        return {
            "pre_equity": pre_equity,
            "post_equity": post_equity,
            "impact": impact,
            "impact_pct": impact / pre_equity if pre_equity > 0 else 0.0,
            "pre_exposure": pre_exposure,
            "post_exposure": pre_exposure * (1 + shock_pct),
            "positions_affected": pre_positions,
            "shock_pct": shock_pct,
        }

    def _estimate_portfolio_var(self, portfolio: Portfolio, confidence: float) -> float:
        """Estimate portfolio VaR from position exposures."""
        equity = portfolio.total_equity
        if equity <= 0:
            return 0.0

        total_risk = 0.0
        for pos in portfolio.positions.values():
            weight = pos.market_value / equity if equity > 0 else 0.0
            estimated_vol = 0.02
            total_risk += (weight * estimated_vol) ** 2

        portfolio_vol = math.sqrt(total_risk)
        z_score = 1.645 if confidence == 0.95 else 2.326 if confidence == 0.99 else 1.96

        return portfolio_vol * z_score

    def _estimate_portfolio_volatility(self, portfolio: Portfolio) -> float:
        """Estimate annualized portfolio volatility."""
        equity = portfolio.total_equity
        if equity <= 0:
            return 0.0

        total_risk = 0.0
        for pos in portfolio.positions.values():
            weight = pos.market_value / equity if equity > 0 else 0.0
            estimated_vol = 0.02
            total_risk += (weight * estimated_vol) ** 2

        daily_vol = math.sqrt(total_risk)
        return daily_vol * math.sqrt(252)

    def _calculate_kelly(self, portfolio: Portfolio) -> float:
        """Estimate Kelly criterion for optimal position sizing."""
        equity = portfolio.total_equity
        if equity <= 0 or not portfolio.positions:
            return 0.0

        total_pnl = sum(p.unrealized_pnl for p in portfolio.positions.values())
        wins = sum(1 for p in portfolio.positions.values() if p.unrealized_pnl > 0)
        total = len(portfolio.positions)

        if total == 0:
            return 0.0

        win_rate = wins / total
        avg_win = total_pnl / wins if wins > 0 else 0.0
        avg_loss = abs(total_pnl / (total - wins)) if total - wins > 0 else 1.0

        if avg_loss == 0:
            return 0.0

        win_loss_ratio = abs(avg_win / avg_loss)
        kelly = win_rate - ((1 - win_rate) / win_loss_ratio)

        return max(0.0, min(kelly, 0.25))

    def _calculate_risk_score(
        self,
        concentration: float,
        max_pos_pct: float,
        drawdown: float,
        var_95: float,
    ) -> str:
        """Calculate an overall risk score from 1 (low) to 5 (high)."""
        score = 1

        if concentration > 0.5:
            score += 1
        if concentration > 0.8:
            score += 1

        if max_pos_pct > 0.15:
            score += 1
        if max_pos_pct > 0.25:
            score += 1

        if drawdown > 0.10:
            score += 1

        if var_95 > 0.03:
            score += 1

        score = min(score, 5)
        labels = {1: "LOW", 2: "MODERATE", 3: "ELEVATED", 4: "HIGH", 5: "CRITICAL"}
        return labels.get(score, "UNKNOWN")

    def _empty_report(self, warnings: list[str]) -> RiskReport:
        """Return a zero-valued risk report."""
        return RiskReport(
            portfolio_var_95=0.0,
            portfolio_var_99=0.0,
            portfolio_volatility=0.0,
            position_concentration=0.0,
            max_position_pct=0.0,
            correlation_risk=0.0,
            tail_risk=0.0,
            kelly_fraction=0.0,
            risk_score="UNKNOWN",
            warnings=warnings,
        )
