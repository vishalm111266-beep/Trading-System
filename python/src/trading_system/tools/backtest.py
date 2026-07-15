"""Backtesting engine for strategy evaluation on historical data."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Protocol

from trading_system.models.candle import Candle
from trading_system.models.symbol import Symbol
from trading_system.portfolio.portfolio import Portfolio
from trading_system.portfolio.position import Side
from trading_system.strategies.base import Strategy
from trading_system.strategies.signal import SignalType

logger = logging.getLogger(__name__)


class DataProvider(Protocol):
    """Protocol for historical data providers."""

    def fetch_candles(
        self, symbol: Symbol, start: datetime, end: datetime
    ) -> list[Candle]: ...


@dataclass(frozen=True, slots=True)
class TradeRecord:
    """Single trade executed during backtest."""

    symbol: Symbol
    side: Side
    entry_date: datetime
    exit_date: datetime
    entry_price: float
    exit_price: float
    quantity: int
    pnl: float
    pnl_pct: float


@dataclass
class BacktestResult:
    """Complete backtest results with performance metrics."""

    trades: list[TradeRecord] = field(default_factory=list)
    equity_curve: list[tuple[datetime, float]] = field(default_factory=list)
    initial_capital: float = 0.0
    final_equity: float = 0.0
    total_return_pct: float = 0.0
    max_drawdown_pct: float = 0.0
    win_rate: float = 0.0
    profit_factor: float = 0.0
    sharpe_ratio: float = 0.0
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0

    @property
    def avg_trade_pnl(self) -> float:
        """Average P&L per trade."""
        if not self.trades:
            return 0.0
        return sum(t.pnl for t in self.trades) / len(self.trades)

    @property
    def avg_win(self) -> float:
        """Average P&L of winning trades."""
        wins = [t.pnl for t in self.trades if t.pnl > 0]
        return sum(wins) / len(wins) if wins else 0.0

    @property
    def avg_loss(self) -> float:
        """Average P&L of losing trades."""
        losses = [t.pnl for t in self.trades if t.pnl < 0]
        return sum(losses) / len(losses) if losses else 0.0


class BacktestEngine:
    """Run a strategy against historical data and track performance.

    Usage::

        engine = BacktestEngine(initial_capital=100_000)
        result = engine.run(strategy, candles_by_symbol, start, end)
    """

    def __init__(
        self,
        initial_capital: float = 100_000.0,
        position_size_pct: float = 0.10,
        commission_pct: float = 0.001,
        slippage_pct: float = 0.001,
    ) -> None:
        if initial_capital <= 0:
            msg = f"initial_capital must be positive, got {initial_capital}"
            raise ValueError(msg)
        if not 0 < position_size_pct <= 1:
            msg = f"position_size_pct must be in (0, 1], got {position_size_pct}"
            raise ValueError(msg)

        self.initial_capital = initial_capital
        self.position_size_pct = position_size_pct
        self.commission_pct = commission_pct
        self.slippage_pct = slippage_pct

    def run(
        self,
        strategy: Strategy,
        candles_by_symbol: dict[Symbol, list[Candle]],
        start: datetime,
        end: datetime,
    ) -> BacktestResult:
        """Execute backtest over the given date range.

        Args:
            strategy: Strategy to evaluate.
            candles_by_symbol: Historical candles keyed by symbol.
            start: Backtest start date (inclusive).
            end: Backtest end date (inclusive).

        Returns:
            BacktestResult with all trades and performance metrics.
        """
        portfolio = Portfolio(cash=self.initial_capital)
        trades: list[TradeRecord] = []
        equity_curve: list[tuple[datetime, float]] = []
        open_entries: dict[Symbol, tuple[datetime, float, int]] = {}

        all_dates = self._collect_dates(candles_by_symbol, start, end)

        for date in all_dates:
            current_prices = self._get_prices_at_date(candles_by_symbol, date)
            portfolio.update_prices(current_prices)

            for symbol in list(portfolio.positions.keys()):
                if symbol in current_prices:
                    self._check_stop_loss(
                        portfolio, symbol, current_prices[symbol],
                        date, trades, open_entries
                    )

            signals = self._evaluate_signals(strategy, candles_by_symbol, date, current_prices)

            for signal in signals:
                is_buy = signal.signal_type == SignalType.BUY
                not_held = signal.symbol not in portfolio.positions
                if is_buy and not_held:
                    self._open_position(
                        portfolio, signal.symbol, current_prices, date, open_entries
                    )
                elif signal.signal_type == SignalType.SELL and signal.symbol in portfolio.positions:
                    self._close_position(
                        portfolio, signal.symbol, current_prices, date, trades, open_entries
                    )

            equity_curve.append((date, portfolio.total_equity))

        self._close_all_positions(portfolio, current_prices, end, trades, open_entries)

        return self._build_result(
            portfolio, trades, equity_curve
        )

    def _collect_dates(
        self,
        candles_by_symbol: dict[Symbol, list[Candle]],
        start: datetime,
        end: datetime,
    ) -> list[datetime]:
        """Collect all unique dates across symbols within range."""
        dates: set[datetime] = set()
        for candles in candles_by_symbol.values():
            for candle in candles:
                if start <= candle.timestamp <= end:
                    dates.add(candle.timestamp)
        return sorted(dates)

    def _get_prices_at_date(
        self,
        candles_by_symbol: dict[Symbol, list[Candle]],
        date: datetime,
    ) -> dict[Symbol, float]:
        """Get closing prices for all symbols at a given date."""
        prices: dict[Symbol, float] = {}
        for symbol, candles in candles_by_symbol.items():
            for candle in candles:
                if candle.timestamp == date:
                    prices[symbol] = candle.close
                    break
        return prices

    def _evaluate_signals(
        self,
        strategy: Strategy,
        candles_by_symbol: dict[Symbol, list[Candle]],
        date: datetime,
        current_prices: dict[Symbol, float],
    ) -> list:
        """Evaluate strategy signals at a given date (simplified)."""
        from trading_system.scanner.result import RankingEntry, RankingTable, ScanResult

        signals: list = []
        for symbol, candles in candles_by_symbol.items():
            window = [c for c in candles if c.timestamp <= date][-20:]
            if len(window) < 5 or symbol not in current_prices:
                continue

            ranking = RankingTable(
                entries=[
                    RankingEntry(
                        symbol=symbol,
                        rank=1,
                        score=current_prices[symbol],
                    )
                ]
            )
            result = ScanResult(ranking=ranking, details=[])

            try:
                evaluated = strategy.evaluate(result)
                if evaluated:
                    signals.append(evaluated[0])
            except Exception:
                continue

        return signals

    def _open_position(
        self,
        portfolio: Portfolio,
        symbol: Symbol,
        current_prices: dict[Symbol, float],
        date: datetime,
        open_entries: dict[Symbol, tuple[datetime, float, int]],
    ) -> None:
        """Open a new position with position sizing."""
        if symbol not in current_prices:
            return

        price = current_prices[symbol]
        price_with_slippage = price * (1 + self.slippage_pct)

        max_dollars = portfolio.total_equity * self.position_size_pct
        available = min(max_dollars, portfolio.cash * 0.95)

        if available <= 0:
            return

        quantity = int(available / price_with_slippage)
        if quantity <= 0:
            return

        cost = quantity * price_with_slippage
        commission = cost * self.commission_pct

        if cost + commission > portfolio.cash:
            return

        portfolio.add_position(symbol, Side.LONG, quantity, price_with_slippage)
        portfolio.cash -= commission
        open_entries[symbol] = (date, price_with_slippage, quantity)
        logger.debug("OPEN %s %d @ %.2f on %s", symbol, quantity, price_with_slippage, date.date())

    def _close_position(
        self,
        portfolio: Portfolio,
        symbol: Symbol,
        current_prices: dict[Symbol, float],
        date: datetime,
        trades: list[TradeRecord],
        open_entries: dict[Symbol, tuple[datetime, float, int]],
    ) -> None:
        """Close an existing position."""
        if symbol not in current_prices or symbol not in portfolio.positions:
            return

        price = current_prices[symbol]
        price_with_slippage = price * (1 - self.slippage_pct)

        pos = portfolio.positions[symbol]
        default = (date, pos.entry_price, pos.quantity)
        entry_date, entry_price, quantity = open_entries.pop(symbol, default)

        realized = portfolio.remove_position(symbol, price_with_slippage)
        commission = quantity * price_with_slippage * self.commission_pct
        realized -= commission

        pnl_pct = realized / (quantity * entry_price) if entry_price > 0 else 0.0

        trades.append(
            TradeRecord(
                symbol=symbol,
                side=Side.LONG,
                entry_date=entry_date,
                exit_date=date,
                entry_price=entry_price,
                exit_price=price_with_slippage,
                quantity=quantity,
                pnl=realized,
                pnl_pct=pnl_pct,
            )
        )
        logger.debug(
            "CLOSE %s %d @ %.2f | PnL: %.2f",
            symbol, quantity, price_with_slippage, realized
        )

    def _close_all_positions(
        self,
        portfolio: Portfolio,
        current_prices: dict[Symbol, float],
        date: datetime,
        trades: list[TradeRecord],
        open_entries: dict[Symbol, tuple[datetime, float, int]],
    ) -> None:
        """Close all remaining positions at end of backtest."""
        for symbol in list(portfolio.positions.keys()):
            self._close_position(portfolio, symbol, current_prices, date, trades, open_entries)

    def _check_stop_loss(
        self,
        portfolio: Portfolio,
        symbol: Symbol,
        current_price: float,
        date: datetime,
        trades: list[TradeRecord],
        open_entries: dict[Symbol, tuple[datetime, float, int]],
    ) -> None:
        """Close position if stop loss triggered (10% from entry)."""
        if symbol not in portfolio.positions:
            return

        pos = portfolio.positions[symbol]
        loss_pct = (pos.entry_price - current_price) / pos.entry_price

        if loss_pct >= 0.10:
            self._close_position(
                portfolio, symbol, {symbol: current_price},
                date, trades, open_entries
            )

    def _build_result(
        self,
        portfolio: Portfolio,
        trades: list[TradeRecord],
        equity_curve: list[tuple[datetime, float]],
    ) -> BacktestResult:
        """Build final BacktestResult from completed trades."""
        final_equity = portfolio.total_equity
        total_return = (final_equity - self.initial_capital) / self.initial_capital

        winning = [t for t in trades if t.pnl > 0]
        losing = [t for t in trades if t.pnl < 0]

        win_rate = len(winning) / len(trades) if trades else 0.0

        gross_profit = sum(t.pnl for t in winning)
        gross_loss = abs(sum(t.pnl for t in losing))
        if gross_loss > 0:
            profit_factor = gross_profit / gross_loss
        elif gross_profit > 0:
            profit_factor = float("inf")
        else:
            profit_factor = 0.0

        max_dd = self._calculate_max_drawdown(equity_curve)
        sharpe = self._calculate_sharpe(equity_curve)

        return BacktestResult(
            trades=trades,
            equity_curve=equity_curve,
            initial_capital=self.initial_capital,
            final_equity=final_equity,
            total_return_pct=total_return,
            max_drawdown_pct=max_dd,
            win_rate=win_rate,
            profit_factor=profit_factor,
            sharpe_ratio=sharpe,
            total_trades=len(trades),
            winning_trades=len(winning),
            losing_trades=len(losing),
        )

    def _calculate_max_drawdown(self, equity_curve: list[tuple[datetime, float]]) -> float:
        """Calculate maximum drawdown from equity curve."""
        if len(equity_curve) < 2:
            return 0.0

        peak = equity_curve[0][1]
        max_dd = 0.0

        for _, equity in equity_curve:
            if equity > peak:
                peak = equity
            dd = (peak - equity) / peak if peak > 0 else 0.0
            if dd > max_dd:
                max_dd = dd

        return max_dd

    def _calculate_sharpe(
        self,
        equity_curve: list[tuple[datetime, float]],
        risk_free_rate: float = 0.02,
    ) -> float:
        """Calculate annualized Sharpe ratio."""
        if len(equity_curve) < 2:
            return 0.0

        returns = []
        for i in range(1, len(equity_curve)):
            prev_eq = equity_curve[i - 1][1]
            curr_eq = equity_curve[i][1]
            if prev_eq > 0:
                returns.append((curr_eq - prev_eq) / prev_eq)

        if not returns:
            return 0.0

        avg_return = sum(returns) / len(returns)
        variance = sum((r - avg_return) ** 2 for r in returns) / len(returns)
        std_dev = variance ** 0.5

        if std_dev == 0:
            return 0.0

        daily_rf = risk_free_rate / 252
        return (avg_return - daily_rf) / std_dev * (252 ** 0.5)
