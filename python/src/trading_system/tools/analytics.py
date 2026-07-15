"""Performance analytics for trading strategies and portfolios."""

from __future__ import annotations

import math
from dataclasses import dataclass

from trading_system.tools.backtest import BacktestResult, TradeRecord


@dataclass(frozen=True, slots=True)
class PerformanceMetrics:
    """Comprehensive performance metrics for a trading strategy."""

    total_return_pct: float
    annualized_return_pct: float
    max_drawdown_pct: float
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    win_rate: float
    profit_factor: float
    avg_win: float
    avg_loss: float
    win_loss_ratio: float
    total_trades: int
    avg_holding_days: float
    max_consecutive_losses: int
    expectancy: float

    def summary(self) -> str:
        """Return a formatted summary string."""
        return (
            f"Total Return: {self.total_return_pct:.2%}\n"
            f"Annualized Return: {self.annualized_return_pct:.2%}\n"
            f"Max Drawdown: {self.max_drawdown_pct:.2%}\n"
            f"Sharpe Ratio: {self.sharpe_ratio:.2f}\n"
            f"Sortino Ratio: {self.sortino_ratio:.2f}\n"
            f"Calmar Ratio: {self.calmar_ratio:.2f}\n"
            f"Win Rate: {self.win_rate:.2%}\n"
            f"Profit Factor: {self.profit_factor:.2f}\n"
            f"Avg Win: {self.avg_win:.2f}\n"
            f"Avg Loss: {self.avg_loss:.2f}\n"
            f"Win/Loss Ratio: {self.win_loss_ratio:.2f}\n"
            f"Total Trades: {self.total_trades}\n"
            f"Avg Holding Days: {self.avg_holding_days:.1f}\n"
            f"Max Consecutive Losses: {self.max_consecutive_losses}\n"
            f"Expectancy: {self.expectancy:.2f}"
        )


def calculate_metrics(
    result: BacktestResult, trading_days_per_year: int = 252
) -> PerformanceMetrics:
    """Calculate comprehensive performance metrics from backtest results."""
    if not result.trades:
        return _empty_metrics()

    trades = result.trades
    total_trades = len(trades)

    winning = [t for t in trades if t.pnl > 0]
    losing = [t for t in trades if t.pnl < 0]

    win_rate = len(winning) / total_trades

    avg_win = sum(t.pnl for t in winning) / len(winning) if winning else 0.0
    avg_loss = sum(t.pnl for t in losing) / len(losing) if losing else 0.0

    gross_profit = sum(t.pnl for t in winning)
    gross_loss = abs(sum(t.pnl for t in losing))
    if gross_loss > 0:
        profit_factor = gross_profit / gross_loss
    elif gross_profit > 0:
        profit_factor = float("inf")
    else:
        profit_factor = 0.0

    win_loss_ratio = abs(avg_win / avg_loss) if avg_loss != 0 else float("inf")

    total_pnl = sum(t.pnl for t in trades)
    total_cost = sum(t.entry_price * t.quantity for t in trades)
    total_return = total_pnl / total_cost if total_cost > 0 else 0.0

    if len(result.equity_curve) >= 2:
        first_date = result.equity_curve[0][0]
        last_date = result.equity_curve[-1][0]
        years = max((last_date - first_date).days / 365.25, 0.01)
    else:
        years = 1.0

    annualized = (1 + total_return) ** (1 / years) - 1 if years > 0 else 0.0

    daily_returns = _calculate_daily_returns(result.equity_curve)
    sharpe = _calculate_sharpe_ratio(daily_returns)
    sortino = _calculate_sortino_ratio(daily_returns)
    calmar = annualized / result.max_drawdown_pct if result.max_drawdown_pct > 0 else 0.0

    avg_holding = _calculate_avg_holding_days(trades)
    max_consec_losses = _calculate_max_consecutive_losses(trades)

    expectancy = (win_rate * avg_win) + ((1 - win_rate) * avg_loss)

    return PerformanceMetrics(
        total_return_pct=total_return,
        annualized_return_pct=annualized,
        max_drawdown_pct=result.max_drawdown_pct,
        sharpe_ratio=sharpe,
        sortino_ratio=sortino,
        calmar_ratio=calmar,
        win_rate=win_rate,
        profit_factor=profit_factor,
        avg_win=avg_win,
        avg_loss=avg_loss,
        win_loss_ratio=win_loss_ratio,
        total_trades=total_trades,
        avg_holding_days=avg_holding,
        max_consecutive_losses=max_consec_losses,
        expectancy=expectancy,
    )


def _empty_metrics() -> PerformanceMetrics:
    """Return zero-valued metrics when no trades exist."""
    return PerformanceMetrics(
        total_return_pct=0.0,
        annualized_return_pct=0.0,
        max_drawdown_pct=0.0,
        sharpe_ratio=0.0,
        sortino_ratio=0.0,
        calmar_ratio=0.0,
        win_rate=0.0,
        profit_factor=0.0,
        avg_win=0.0,
        avg_loss=0.0,
        win_loss_ratio=0.0,
        total_trades=0,
        avg_holding_days=0.0,
        max_consecutive_losses=0,
        expectancy=0.0,
    )


def _calculate_daily_returns(equity_curve: list[tuple]) -> list[float]:
    """Calculate daily returns from equity curve."""
    if len(equity_curve) < 2:
        return []

    returns = []
    for i in range(1, len(equity_curve)):
        prev = equity_curve[i - 1][1]
        curr = equity_curve[i][1]
        if prev > 0:
            returns.append((curr - prev) / prev)
    return returns


def _calculate_sharpe_ratio(daily_returns: list[float], risk_free_rate: float = 0.02) -> float:
    """Calculate annualized Sharpe ratio."""
    if not daily_returns:
        return 0.0

    avg = sum(daily_returns) / len(daily_returns)
    variance = sum((r - avg) ** 2 for r in daily_returns) / len(daily_returns)
    std = math.sqrt(variance)

    if std == 0:
        return 0.0

    daily_rf = risk_free_rate / 252
    return (avg - daily_rf) / std * math.sqrt(252)


def _calculate_sortino_ratio(daily_returns: list[float], risk_free_rate: float = 0.02) -> float:
    """Calculate annualized Sortino ratio (penalizes only downside volatility)."""
    if not daily_returns:
        return 0.0

    avg = sum(daily_returns) / len(daily_returns)
    downside_returns = [r for r in daily_returns if r < 0]

    if not downside_returns:
        return float("inf") if avg > 0 else 0.0

    downside_variance = sum(r ** 2 for r in downside_returns) / len(downside_returns)
    downside_std = math.sqrt(downside_variance)

    if downside_std == 0:
        return 0.0

    daily_rf = risk_free_rate / 252
    return (avg - daily_rf) / downside_std * math.sqrt(252)


def _calculate_avg_holding_days(trades: list[TradeRecord]) -> float:
    """Calculate average holding period in days."""
    if not trades:
        return 0.0

    total_days = sum((t.exit_date - t.entry_date).days for t in trades)
    return total_days / len(trades)


def _calculate_max_consecutive_losses(trades: list[TradeRecord]) -> int:
    """Calculate maximum consecutive losing trades."""
    max_streak = 0
    current_streak = 0

    for trade in trades:
        if trade.pnl < 0:
            current_streak += 1
            if current_streak > max_streak:
                max_streak = current_streak
        else:
            current_streak = 0

    return max_streak


def calculate_rolling_sharpe(
    equity_curve: list[tuple], window: int = 63, risk_free_rate: float = 0.02
) -> list[tuple]:
    """Calculate rolling Sharpe ratio over a given window (in trading days)."""
    if len(equity_curve) < window + 1:
        return []

    daily_returns = _calculate_daily_returns(equity_curve)
    rolling_sharpe: list[tuple] = []

    for i in range(window - 1, len(daily_returns)):
        window_returns = daily_returns[i - window + 1 : i + 1]
        avg = sum(window_returns) / len(window_returns)
        variance = sum((r - avg) ** 2 for r in window_returns) / len(window_returns)
        std = math.sqrt(variance)

        if std > 0:
            daily_rf = risk_free_rate / 252
            sharpe = (avg - daily_rf) / std * math.sqrt(252)
        else:
            sharpe = 0.0

        date = equity_curve[i + 1][0]
        rolling_sharpe.append((date, sharpe))

    return rolling_sharpe


def calculate_monthly_returns(equity_curve: list[tuple]) -> list[tuple[str, float]]:
    """Group equity curve into monthly returns."""
    if len(equity_curve) < 2:
        return []

    monthly: dict[str, float] = {}

    for date, equity in equity_curve:
        month_key = date.strftime("%Y-%m")
        if month_key not in monthly:
            monthly[month_key] = equity
        monthly[month_key] = equity

    results: list[tuple[str, float]] = []
    prev_equity = equity_curve[0][1]

    for month_key in sorted(monthly.keys()):
        curr_equity = monthly[month_key]
        ret = (curr_equity - prev_equity) / prev_equity if prev_equity > 0 else 0.0
        results.append((month_key, ret))
        prev_equity = curr_equity

    return results
