"""Provider session lifecycle management."""

from __future__ import annotations

import logging
from types import TracebackType

from trading_system.data.provider import Provider

logger = logging.getLogger(__name__)


class Session:
    """Context manager that connects and disconnects a provider."""

    def __init__(self, provider: Provider) -> None:
        self._provider = provider

    @property
    def provider(self) -> Provider:
        return self._provider

    def __enter__(self) -> Session:
        logger.debug("connecting provider %s", self._provider.name)
        self._provider.connect()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        logger.debug("disconnecting provider %s", self._provider.name)
        self._provider.disconnect()
