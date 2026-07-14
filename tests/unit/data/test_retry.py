"""Tests for trading_system.data.retry."""

from datetime import datetime

import pytest
from trading_system.data.exceptions import DataSourceError
from trading_system.data.retry import RetryExhausted, with_retry
from trading_system.models.candle import Candle
from trading_system.models.symbol import Symbol

SYMBOL = Symbol(raw="AAPL")
TS = datetime(2025, 1, 1)


def _ok_candle() -> list[Candle]:
    return [
        Candle(
            timestamp=datetime(2025, 1, 2),
            open=100, high=110, low=95, close=105, volume=1000,
        ),
    ]


class TestWithRetry:
    def test_success_on_first_try(self) -> None:
        call_count = 0

        def op() -> list[Candle]:
            nonlocal call_count
            call_count += 1
            return _ok_candle()

        wrapped = with_retry(op, max_attempts=3)
        result = wrapped()
        assert len(result) == 1
        assert call_count == 1

    def test_retries_on_failure(self) -> None:
        call_count = 0

        def op() -> list[Candle]:
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise DataSourceError("transient")
            return _ok_candle()

        wrapped = with_retry(op, max_attempts=3, delay=0.01)
        result = wrapped()
        assert len(result) == 1
        assert call_count == 3

    def test_exhausts_and_raises(self) -> None:
        def op() -> None:
            raise DataSourceError("permanent")

        wrapped = with_retry(op, max_attempts=2, delay=0.01)
        with pytest.raises(RetryExhausted, match="2 attempts"):
            wrapped()

    def test_max_attempts_one(self) -> None:
        call_count = 0

        def op() -> int:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise DataSourceError("fail")
            return 42

        wrapped = with_retry(op, max_attempts=1, delay=0.01)
        with pytest.raises(RetryExhausted):
            wrapped()
        assert call_count == 1

    def test_invalid_max_attempts(self) -> None:
        with pytest.raises(ValueError, match="max_attempts"):
            with_retry(lambda: None, max_attempts=0)

    def test_preserves_function_name(self) -> None:
        def my_func() -> int:
            return 42

        wrapped = with_retry(my_func, max_attempts=1, delay=0.01)
        assert wrapped.__name__ == "my_func"

    def test_non_datasource_error_propagates(self) -> None:
        def op() -> None:
            raise TypeError("not my problem")

        wrapped = with_retry(op, max_attempts=3, delay=0.01)
        with pytest.raises(TypeError):
            wrapped()
