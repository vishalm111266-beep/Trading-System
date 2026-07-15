"""Market data utilities for fetching, loading, and analyzing price data."""

from __future__ import annotations

import csv
import logging
from datetime import datetime
from pathlib import Path

from trading_system.data.provider import Provider, ProviderRegistry
from trading_system.models.candle import Candle
from trading_system.models.symbol import Symbol

logger = logging.getLogger(__name__)


def get_default_provider() -> Provider | None:
    """Get the default data provider from registry."""
    names = ProviderRegistry.names()
    if not names:
        logger.warning("no providers registered")
        return None

    for name in ["csv", "yahoo", "kite"]:
        if name in names:
            cls = ProviderRegistry.get(name)
            if cls:
                provider = cls()
                try:
                    provider.connect()
                    if provider.is_available():
                        return provider
                except Exception:
                    continue

    cls = ProviderRegistry.get(names[0])
    if cls:
        return cls()
    return None


def fetch_candles(
    symbol: Symbol,
    start: datetime,
    end: datetime,
    provider: Provider | None = None,
) -> list[Candle]:
    """Fetch candles for a symbol using the given or default provider."""
    if provider is None:
        provider = get_default_provider()
    if provider is None:
        msg = "no data provider available"
        raise RuntimeError(msg)

    try:
        provider.connect()
        return provider.fetch_candles(symbol, start, end)
    finally:
        try:
            provider.disconnect()
        except Exception:
            pass


def load_candles_from_csv(filepath: str | Path) -> list[Candle]:
    """Load candles from a CSV file.

    Expected columns: timestamp, open, high, low, close, volume
    Timestamp format: YYYY-MM-DD or YYYY-MM-DD HH:MM:SS
    """
    filepath = Path(filepath)
    if not filepath.exists():
        msg = f"CSV file not found: {filepath}"
        raise FileNotFoundError(msg)

    candles: list[Candle] = []

    with open(filepath, newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:
            try:
                ts_str = row["timestamp"]
                if len(ts_str) <= 10:
                    ts = datetime.strptime(ts_str, "%Y-%m-%d")
                else:
                    ts = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")

                candle = Candle(
                    timestamp=ts,
                    open=float(row["open"]),
                    high=float(row["high"]),
                    low=float(row["low"]),
                    close=float(row["close"]),
                    volume=float(row["volume"]),
                )
                candles.append(candle)
            except (KeyError, ValueError) as e:
                logger.warning("skipping malformed row: %s", e)
                continue

    candles.sort(key=lambda c: c.timestamp)
    return candles


def save_candles_to_csv(candles: list[Candle], filepath: str | Path) -> None:
    """Save candles to a CSV file."""
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["timestamp", "open", "high", "low", "close", "volume"],
        )
        writer.writeheader()

        for candle in sorted(candles, key=lambda c: c.timestamp):
            writer.writerow({
                "timestamp": candle.timestamp.strftime("%Y-%m-%d"),
                "open": candle.open,
                "high": candle.high,
                "low": candle.low,
                "close": candle.close,
                "volume": candle.volume,
            })


def calculate_sma(candles: list[Candle], period: int) -> list[tuple[datetime, float]]:
    """Calculate Simple Moving Average for closing prices."""
    if len(candles) < period:
        return []

    closes = [(c.timestamp, c.close) for c in sorted(candles, key=lambda c: c.timestamp)]
    result: list[tuple[datetime, float]] = []

    for i in range(period - 1, len(closes)):
        window = closes[i - period + 1 : i + 1]
        avg = sum(price for _, price in window) / period
        result.append((closes[i][0], avg))

    return result


def calculate_ema(candles: list[Candle], period: int) -> list[tuple[datetime, float]]:
    """Calculate Exponential Moving Average for closing prices."""
    if len(candles) < period:
        return []

    sorted_candles = sorted(candles, key=lambda c: c.timestamp)
    multiplier = 2 / (period + 1)

    ema_values: list[tuple[datetime, float]] = []

    first_window = [c.close for c in sorted_candles[:period]]
    first_ema = sum(first_window) / period
    ema_values.append((sorted_candles[period - 1].timestamp, first_ema))

    for i in range(period, len(sorted_candles)):
        price = sorted_candles[i].close
        prev_ema = ema_values[-1][1]
        new_ema = (price - prev_ema) * multiplier + prev_ema
        ema_values.append((sorted_candles[i].timestamp, new_ema))

    return ema_values


def calculate_rsi(candles: list[Candle], period: int = 14) -> list[tuple[datetime, float]]:
    """Calculate Relative Strength Index for closing prices."""
    if len(candles) < period + 1:
        return []

    sorted_candles = sorted(candles, key=lambda c: c.timestamp)
    closes = [c.close for c in sorted_candles]

    deltas = [closes[i] - closes[i - 1] for i in range(1, len(closes))]
    gains = [max(d, 0) for d in deltas]
    losses = [abs(min(d, 0)) for d in deltas]

    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period

    result: list[tuple[datetime, float]] = []

    if avg_loss == 0:
        rsi = 100.0
    else:
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

    result.append((sorted_candles[period].timestamp, rsi))

    for i in range(period, len(deltas)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period

        if avg_loss == 0:
            rsi = 100.0
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))

        result.append((sorted_candles[i + 1].timestamp, rsi))

    return result


def calculate_atr(candles: list[Candle], period: int = 14) -> list[tuple[datetime, float]]:
    """Calculate Average True Range."""
    if len(candles) < period + 1:
        return []

    sorted_candles = sorted(candles, key=lambda c: c.timestamp)
    true_ranges: list[float] = []

    for i in range(1, len(sorted_candles)):
        high = sorted_candles[i].high
        low = sorted_candles[i].low
        prev_close = sorted_candles[i - 1].close

        tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
        true_ranges.append(tr)

    if len(true_ranges) < period:
        return []

    atr_values: list[tuple[datetime, float]] = []

    current_atr = sum(true_ranges[:period]) / period
    atr_values.append((sorted_candles[period].timestamp, current_atr))

    for i in range(period, len(true_ranges)):
        current_atr = (current_atr * (period - 1) + true_ranges[i]) / period
        atr_values.append((sorted_candles[i + 1].timestamp, current_atr))

    return atr_values


def calculate_bollinger_bands(
    candles: list[Candle], period: int = 20, std_dev: float = 2.0
) -> list[tuple[datetime, float, float, float]]:
    """Calculate Bollinger Bands (upper, middle, lower)."""
    if len(candles) < period:
        return []

    sorted_candles = sorted(candles, key=lambda c: c.timestamp)
    result: list[tuple[datetime, float, float, float]] = []

    for i in range(period - 1, len(sorted_candles)):
        window = [c.close for c in sorted_candles[i - period + 1 : i + 1]]
        middle = sum(window) / period
        variance = sum((x - middle) ** 2 for x in window) / period
        std = variance ** 0.5

        upper = middle + std_dev * std
        lower = middle - std_dev * std

        result.append((sorted_candles[i].timestamp, upper, middle, lower))

    return result
