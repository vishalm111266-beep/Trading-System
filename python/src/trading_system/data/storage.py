"""Persistent storage abstraction for market data."""

from __future__ import annotations

import csv
import logging
from datetime import datetime
from pathlib import Path

from trading_system.models.candle import Candle
from trading_system.models.symbol import Symbol

logger = logging.getLogger(__name__)

_CSV_HEADER = ["timestamp", "open", "high", "low", "close", "volume"]


def _candle_to_row(candle: Candle) -> list:
    return [
        candle.timestamp.isoformat(),
        candle.open,
        candle.high,
        candle.low,
        candle.close,
        candle.volume,
    ]


def _row_to_candle(row: dict[str, str]) -> Candle:
    return Candle(
        timestamp=datetime.fromisoformat(row["timestamp"]),
        open=float(row["open"]),
        high=float(row["high"]),
        low=float(row["low"]),
        close=float(row["close"]),
        volume=float(row["volume"]),
    )


class Storage:
    """Read and write candle data as CSV files on disk."""

    def __init__(self, base_dir: Path) -> None:
        self._base = base_dir

    def _dir_for(self, symbol: Symbol) -> Path:
        d = self._base / symbol.raw.lower()
        d.mkdir(parents=True, exist_ok=True)
        return d

    def _path_for(self, symbol: Symbol, start: datetime, end: datetime) -> Path:
        fname = f"{start:%Y%m%d}_{end:%Y%m%d}.csv"
        return self._dir_for(symbol) / fname

    def read(
        self, symbol: Symbol, start: datetime, end: datetime
    ) -> list[Candle] | None:
        """Load candles from a CSV file. Returns ``None`` if not found."""
        path = self._path_for(symbol, start, end)
        if not path.exists():
            return None
        candles: list[Candle] = []
        with path.open(newline="") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                candles.append(_row_to_candle(row))
        logger.debug("read %d candles from %s", len(candles), path)
        return candles

    def write(
        self, symbol: Symbol, start: datetime, end: datetime, candles: list[Candle]
    ) -> Path:
        """Persist candles to a CSV file. Returns the file path."""
        path = self._path_for(symbol, start, end)
        with path.open("w", newline="") as fh:
            writer = csv.writer(fh)
            writer.writerow(_CSV_HEADER)
            for c in candles:
                writer.writerow(_candle_to_row(c))
        logger.debug("wrote %d candles to %s", len(candles), path)
        return path

    def list_symbols(self) -> list[str]:
        """Return sorted list of symbol directory names."""
        if not self._base.exists():
            return []
        return sorted(
            p.name for p in self._base.iterdir() if p.is_dir()
        )
