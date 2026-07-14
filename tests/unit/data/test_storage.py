"""Tests for trading_system.data.storage."""

from datetime import datetime
from pathlib import Path

from trading_system.data.storage import Storage
from trading_system.models.candle import Candle
from trading_system.models.symbol import Symbol

TS_START = datetime(2025, 1, 1)
TS_END = datetime(2025, 1, 31)
SYMBOL = Symbol(raw="AAPL")


def _candles() -> list[Candle]:
    return [
        Candle(
            timestamp=datetime(2025, 1, 2),
            open=100, high=110, low=95, close=105, volume=1000,
        ),
        Candle(
            timestamp=datetime(2025, 1, 3),
            open=105, high=115, low=100, close=110, volume=1200,
        ),
    ]


class TestStorage:
    def test_write_and_read(self, tmp_path: Path) -> None:
        storage = Storage(tmp_path)
        storage.write(SYMBOL, TS_START, TS_END, _candles())
        result = storage.read(SYMBOL, TS_START, TS_END)
        assert result is not None
        assert len(result) == 2
        assert result[0].open == 100
        assert result[1].volume == 1200

    def test_read_missing_returns_none(self, tmp_path: Path) -> None:
        storage = Storage(tmp_path)
        assert storage.read(SYMBOL, TS_START, TS_END) is None

    def test_creates_symbol_directory(self, tmp_path: Path) -> None:
        storage = Storage(tmp_path)
        storage.write(SYMBOL, TS_START, TS_END, _candles())
        expected = tmp_path / "aapl"
        assert expected.exists()

    def test_csv_file_exists(self, tmp_path: Path) -> None:
        storage = Storage(tmp_path)
        storage.write(SYMBOL, TS_START, TS_END, _candles())
        csv_files = list((tmp_path / "aapl").glob("*.csv"))
        assert len(csv_files) == 1
        content = csv_files[0].read_text()
        assert "timestamp,open,high,low,close,volume" in content

    def test_list_symbols_empty(self, tmp_path: Path) -> None:
        storage = Storage(tmp_path)
        assert storage.list_symbols() == []

    def test_list_symbols(self, tmp_path: Path) -> None:
        storage = Storage(tmp_path)
        storage.write(Symbol(raw="AAPL"), TS_START, TS_END, _candles())
        storage.write(Symbol(raw="MSFT"), TS_START, TS_END, _candles())
        assert storage.list_symbols() == ["aapl", "msft"]

    def test_roundtrip_preserves_types(self, tmp_path: Path) -> None:
        storage = Storage(tmp_path)
        original = _candles()
        storage.write(SYMBOL, TS_START, TS_END, original)
        result = storage.read(SYMBOL, TS_START, TS_END)
        assert result is not None
        for orig, loaded in zip(original, result, strict=True):
            assert orig.timestamp == loaded.timestamp
            assert orig.open == loaded.open
            assert orig.high == loaded.high
            assert orig.low == loaded.low
            assert orig.close == loaded.close
            assert orig.volume == loaded.volume
