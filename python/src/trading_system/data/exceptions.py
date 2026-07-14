"""Data-layer exceptions."""


class DataError(Exception):
    """Base exception for all data-layer errors."""


class DataSourceError(DataError):
    """Raised when a data source request fails."""


class ValidationError(DataError):
    """Raised when data fails validation checks."""


class CacheError(DataError):
    """Raised on cache read/write failures."""


class SymbolNotFoundError(DataError):
    """Raised when a requested symbol has no data."""
