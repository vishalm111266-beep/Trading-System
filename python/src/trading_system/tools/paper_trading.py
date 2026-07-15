"""Paper trading simulator for live strategy testing without real money."""

from __future__ import annotations

import logging
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime

from trading_system.models.symbol import Symbol
from trading_system.portfolio.portfolio import Portfolio
from trading_system.portfolio.position import Side
from trading_system.portfolio.risk import RiskLimits, RiskManager
from trading_system.strategies.signal import Signal, SignalType

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class PaperOrder:
    """Simulated order."""

    order_id: str
    symbol: Symbol
    side: Side
    quantity: int
    order_type: str
    created_at: datetime
    limit_price: float | None = None


@dataclass(frozen=True, slots=True)
class PaperFill:
    """Simulated order fill."""

    order_id: str
    symbol: Symbol
    side: Side
    quantity: int
    fill_price: float
    filled_at: datetime
    commission: float


@dataclass
class PaperTradingEngine:
    """Simulates live trading with paper money.

    Usage::

        engine = PaperTradingEngine(initial_cash=100_000)
        engine.on_signal(my_signal_handler)
        engine.submit_signal(signal)
        engine.update_price(symbol, new_price)
    """

    cash: float
    portfolio: Portfolio = field(init=False)
    risk_manager: RiskManager = field(init=False)
    commission_pct: float = 0.001
    slippage_pct: float = 0.001
    _signal_handlers: list[Callable[[Signal], None]] = field(default_factory=list, init=False)
    _order_history: list[PaperOrder] = field(default_factory=list, init=False)
    _fill_history: list[PaperFill] = field(default_factory=list, init=False)
    _trade_log: list[str] = field(default_factory=list, init=False)

    def __post_init__(self) -> None:
        if self.cash <= 0:
            msg = f"cash must be positive, got {self.cash}"
            raise ValueError(msg)
        self.portfolio = Portfolio(cash=self.cash)
        self.risk_manager = RiskManager(RiskLimits())

    def on_signal(self, handler: Callable[[Signal], None]) -> None:
        """Register a signal handler for notifications."""
        self._signal_handlers.append(handler)

    def submit_signal(self, signal: Signal) -> PaperFill | None:
        """Process a trading signal and execute if valid.

        Returns the fill if a trade was executed, None otherwise.
        """
        for handler in self._signal_handlers:
            handler(signal)

        if signal.signal_type == SignalType.BUY:
            return self._execute_buy(signal.symbol)
        elif signal.signal_type == SignalType.SELL:
            return self._execute_sell(signal.symbol)

        return None

    def _execute_buy(self, symbol: Symbol) -> PaperFill | None:
        """Execute a buy order with position sizing and risk checks."""
        if symbol in self.portfolio.positions:
            logger.debug("already holding %s, skipping buy", symbol)
            return None

        equity = self.portfolio.total_equity
        max_dollars = equity * 0.10
        available = min(max_dollars, self.portfolio.cash * 0.95)

        if not self.risk_manager.check_position_size(available, equity):
            available = self.risk_manager.clamp_position_size(available, equity)

        if available <= 0:
            logger.debug("no available capital for %s", symbol)
            return None

        if symbol in self.portfolio.positions:
            price = self.portfolio.positions[symbol].current_price
        else:
            price = None
        if price is None:
            logger.debug("no price available for %s", symbol)
            return None

        price_with_slippage = price * (1 + self.slippage_pct)
        quantity = int(available / price_with_slippage)

        if quantity <= 0:
            return None

        cost = quantity * price_with_slippage
        commission = cost * self.commission_pct

        if cost + commission > self.portfolio.cash:
            return None

        self.portfolio.add_position(symbol, Side.LONG, quantity, price_with_slippage)
        self.portfolio.cash -= commission

        order = PaperOrder(
            order_id=str(uuid.uuid4())[:8],
            symbol=symbol,
            side=Side.LONG,
            quantity=quantity,
            order_type="MARKET",
            created_at=datetime.now(),
        )
        self._order_history.append(order)

        fill = PaperFill(
            order_id=order.order_id,
            symbol=symbol,
            side=Side.LONG,
            quantity=quantity,
            fill_price=price_with_slippage,
            filled_at=datetime.now(),
            commission=commission,
        )
        self._fill_history.append(fill)

        msg = f"BUY {quantity} {symbol} @ {price_with_slippage:.2f}"
        self._trade_log.append(msg)
        logger.info(msg)

        return fill

    def _execute_sell(self, symbol: Symbol) -> PaperFill | None:
        """Execute a sell order for an existing position."""
        if symbol not in self.portfolio.positions:
            logger.debug("no position in %s to sell", symbol)
            return None

        pos = self.portfolio.positions[symbol]
        current_price = pos.current_price
        price_with_slippage = current_price * (1 - self.slippage_pct)

        realized = self.portfolio.remove_position(symbol, price_with_slippage)
        commission = pos.quantity * price_with_slippage * self.commission_pct
        self.portfolio.cash -= commission

        order = PaperOrder(
            order_id=str(uuid.uuid4())[:8],
            symbol=symbol,
            side=Side.SHORT,
            quantity=pos.quantity,
            order_type="MARKET",
            created_at=datetime.now(),
        )
        self._order_history.append(order)

        fill = PaperFill(
            order_id=order.order_id,
            symbol=symbol,
            side=Side.SHORT,
            quantity=pos.quantity,
            fill_price=price_with_slippage,
            filled_at=datetime.now(),
            commission=commission,
        )
        self._fill_history.append(fill)

        msg = f"SELL {pos.quantity} {symbol} @ {price_with_slippage:.2f} | PnL: {realized:.2f}"
        self._trade_log.append(msg)
        logger.info(msg)

        return fill

    def update_price(self, symbol: Symbol, price: float) -> None:
        """Update the current price for a held position."""
        self.portfolio.update_prices({symbol: price})

    def get_status(self) -> dict:
        """Return current portfolio status."""
        return {
            "cash": self.portfolio.cash,
            "equity": self.portfolio.total_equity,
            "positions": {
                str(sym): {
                    "quantity": pos.quantity,
                    "entry_price": pos.entry_price,
                    "current_price": pos.current_price,
                    "unrealized_pnl": pos.unrealized_pnl,
                    "market_value": pos.market_value,
                }
                for sym, pos in self.portfolio.positions.items()
            },
            "drawdown": self.portfolio.drawdown,
            "total_trades": len(self._fill_history),
        }

    def get_trade_log(self) -> list[str]:
        """Return the full trade log."""
        return list(self._trade_log)

    def get_order_history(self) -> list[PaperOrder]:
        """Return all submitted orders."""
        return list(self._order_history)

    def get_fill_history(self) -> list[PaperFill]:
        """Return all order fills."""
        return list(self._fill_history)

    def reset(self) -> None:
        """Reset the engine to initial state."""
        self.portfolio = Portfolio(cash=self.cash)
        self._order_history.clear()
        self._fill_history.clear()
        self._trade_log.clear()
