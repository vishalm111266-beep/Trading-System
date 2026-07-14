"""Tests for trading_system.indicators.ranking."""

import pytest
from trading_system.indicators.ranking import rank_by_rs, rank_by_zscore
from trading_system.models.symbol import Symbol


def _syms(*names: str) -> list[Symbol]:
    return [Symbol(raw=n) for n in names]


class TestRankByRS:
    def test_basic(self) -> None:
        result = rank_by_rs(_syms("A", "B", "C"), [3.0, 1.0, 2.0])
        assert result.length == 3
        assert result.entries[0].symbol.raw == "A"
        assert result.entries[0].rank == 1
        assert result.entries[2].symbol.raw == "B"
        assert result.entries[2].rank == 3

    def test_empty(self) -> None:
        result = rank_by_rs([], [])
        assert result.empty

    def test_single(self) -> None:
        result = rank_by_rs(_syms("X"), [42.0])
        assert result.length == 1
        assert result.entries[0].score == 42.0

    def test_length_mismatch(self) -> None:
        with pytest.raises(ValueError, match="length mismatch"):
            rank_by_rs(_syms("A", "B"), [1.0])

    def test_equal_scores(self) -> None:
        result = rank_by_rs(_syms("A", "B", "C"), [1.0, 1.0, 1.0])
        assert result.entries[0].rank == 1
        assert result.entries[1].rank == 2
        assert result.entries[2].rank == 3


class TestRankByZscore:
    def test_basic(self) -> None:
        result = rank_by_zscore(_syms("A", "B", "C"), [10.0, 30.0, 20.0])
        assert result.entries[0].symbol.raw == "B"
        assert result.entries[0].rank == 1

    def test_empty(self) -> None:
        result = rank_by_zscore([], [])
        assert result.empty


class TestRankingResult:
    def test_top_n(self) -> None:
        result = rank_by_rs(_syms("A", "B", "C", "D"), [4, 3, 2, 1])
        top2 = result.top_n(2)
        assert top2.length == 2
        assert top2.entries[0].symbol.raw == "A"

    def test_top_n_negative(self) -> None:
        result = rank_by_rs(_syms("A"), [1.0])
        with pytest.raises(ValueError, match="n must be non-negative"):
            result.top_n(-1)
