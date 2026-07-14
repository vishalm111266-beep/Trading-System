"""Provider registry and abstract provider interface."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from trading_system.data.datasource import DataSource
from trading_system.models.candle import Candle
from trading_system.models.symbol import Symbol

logger = logging.getLogger(__name__)


class Provider(DataSource, ABC):
    """Extended data source with metadata and lifecycle hooks."""

    name: str = ""

    @abstractmethod
    def connect(self) -> None:
        """Establish provider connection."""
        ...

    @abstractmethod
    def disconnect(self) -> None:
        """Tear down provider connection."""
        ...

    @abstractmethod
    def is_available(self) -> bool:
        """Return ``True`` if the provider is ready to serve requests."""
        ...

    @abstractmethod
    def fetch_candles(
        self,
        symbol: Symbol,
        start: datetime,
        end: datetime,
    ) -> list[Candle]:
        """Return candles for *symbol* spanning ``[start, end]``."""
        ...

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        if cls.name:
            ProviderRegistry.register(cls.name, cls)


class ProviderRegistry:
    """Global registry mapping provider names to their classes."""

    _providers: dict[str, type[Provider]] = {}

    @classmethod
    def register(cls, name: str, provider_cls: type[Provider]) -> None:
        """Register a provider class under *name*."""
        if name in cls._providers:
            logger.debug("overwriting provider %s", name)
        cls._providers[name] = provider_cls
        logger.debug("registered provider %s", name)

    @classmethod
    def get(cls, name: str) -> type[Provider] | None:
        """Look up a provider class by name."""
        return cls._providers.get(name)

    @classmethod
    def names(cls) -> list[str]:
        """Return sorted list of registered provider names."""
        return sorted(cls._providers)

    @classmethod
    def all(cls) -> dict[str, type[Provider]]:
        """Return a copy of the registry."""
        return dict(cls._providers)

    @classmethod
    def clear(cls) -> None:
        """Remove all registrations (for testing)."""
        cls._providers.clear()
