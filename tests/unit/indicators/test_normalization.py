"""Tests for trading_system.indicators.normalization."""

import pytest
from trading_system.indicators.normalization import min_max, percentile, zscore


class TestZscore:
    def test_basic(self) -> None:
        result = zscore([1, 2, 3, 4, 5])
        assert len(result) == 5
        assert result[2] == pytest.approx(0.0)

    def test_all_same(self) -> None:
        result = zscore([5, 5, 5])
        assert result == [None, None, None]

    def test_empty(self) -> None:
        assert zscore([]) == []

    def test_single(self) -> None:
        assert zscore([1]) == [None]

    def test_two_values(self) -> None:
        result = zscore([0, 1])
        assert result[0] == pytest.approx(-1.0)
        assert result[1] == pytest.approx(1.0)


class TestMinMax:
    def test_basic(self) -> None:
        result = min_max([10, 20, 30])
        assert result == pytest.approx([0.0, 0.5, 1.0])

    def test_all_same(self) -> None:
        result = min_max([5, 5, 5])
        assert result == [0.0, 0.0, 0.0]

    def test_empty(self) -> None:
        assert min_max([]) == []

    def test_two_values(self) -> None:
        result = min_max([0, 100])
        assert result == pytest.approx([0.0, 1.0])


class TestPercentile:
    def test_basic(self) -> None:
        result = percentile([10, 20, 30])
        assert result[0] == pytest.approx(100 / 3)
        assert result[2] == pytest.approx(100.0)

    def test_all_same(self) -> None:
        result = percentile([5, 5, 5])
        assert all(v == pytest.approx(100.0) for v in result)

    def test_empty(self) -> None:
        assert percentile([]) == []
