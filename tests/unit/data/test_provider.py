"""Tests for trading_system.data.provider."""

from datetime import datetime

import pytest
from trading_system.data.datasource import DataSource
from trading_system.data.provider import Provider, ProviderRegistry
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
    ]


class FakeProvider(Provider):
    name = "fake"

    def connect(self) -> None:
        pass

    def disconnect(self) -> None:
        pass

    def is_available(self) -> bool:
        return True

    def fetch_candles(
        self, symbol: Symbol, start: datetime, end: datetime
    ) -> list[Candle]:
        return _candles()


@pytest.fixture(autouse=True)
def _clean_registry() -> None:
    ProviderRegistry.clear()
    yield
    ProviderRegistry.clear()


class TestProviderRegistry:
    def test_register_and_get(self) -> None:
        ProviderRegistry.register("fake", FakeProvider)
        assert ProviderRegistry.get("fake") is FakeProvider

    def test_get_missing_returns_none(self) -> None:
        assert ProviderRegistry.get("nope") is None

    def test_names_sorted(self) -> None:
        ProviderRegistry.register("z", FakeProvider)
        ProviderRegistry.register("a", FakeProvider)
        assert ProviderRegistry.names() == ["a", "z"]

    def test_all_returns_copy(self) -> None:
        ProviderRegistry.register("fake", FakeProvider)
        result = ProviderRegistry.all()
        result.pop("fake")
        assert ProviderRegistry.get("fake") is FakeProvider

    def test_clear(self) -> None:
        ProviderRegistry.register("fake", FakeProvider)
        ProviderRegistry.clear()
        assert ProviderRegistry.get("fake") is None


class TestProviderSubclass:
    def test_auto_registers(self) -> None:
        class AutoProvider(Provider):
            name = "auto"

            def connect(self) -> None:
                pass

            def disconnect(self) -> None:
                pass

            def is_available(self) -> bool:
                return True

            def fetch_candles(
                self, symbol: Symbol, start: datetime, end: datetime
            ) -> list[Candle]:
                return _candles()

        assert ProviderRegistry.get("auto") is AutoProvider

    def test_provider_is_datasource(self) -> None:
        assert issubclass(Provider, DataSource)

    def test_instantiate_and_fetch(self) -> None:
        p = FakeProvider()
        result = p.fetch_candles(SYMBOL, TS_START, TS_END)
        assert len(result) == 1

    def test_is_available(self) -> None:
        assert FakeProvider().is_available() is True
