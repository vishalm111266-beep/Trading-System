"""Trading tools: backtesting, paper trading, analytics, and risk analysis."""

from trading_system.tools.analytics import PerformanceMetrics, calculate_metrics
from trading_system.tools.backtest import BacktestEngine, BacktestResult
from trading_system.tools.market_utils import (
    fetch_candles,
    get_default_provider,
    load_candles_from_csv,
)
from trading_system.tools.paper_trading import PaperTradingEngine
from trading_system.tools.risk_analyzer import RiskAnalyzer, RiskReport

__all__ = [
    "BacktestEngine",
    "BacktestResult",
    "PaperTradingEngine",
    "PerformanceMetrics",
    "RiskAnalyzer",
    "RiskReport",
    "calculate_metrics",
    "fetch_candles",
    "get_default_provider",
    "load_candles_from_csv",
]
