"""Market symbol representation."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Symbol:
    """Immutable market symbol (e.g. ``AAPL``, ``NIFTY 50``)."""

    raw: str
    exchange: str = ""

    def __str__(self) -> str:
        if self.exchange:
            return f"{self.raw}:{self.exchange}"
        return self.raw

    @classmethod
    def from_str(cls, value: str) -> Symbol:
        """Parse ``SYMBOL`` or ``SYMBOL:EXCHANGE``."""
        parts = value.split(":", 1)
        if len(parts) == 2:
            return cls(raw=parts[0].strip().upper(), exchange=parts[1].strip().upper())
        return cls(raw=parts[0].strip().upper())
