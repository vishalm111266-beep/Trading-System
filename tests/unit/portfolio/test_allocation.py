"""Tests for trading_system.portfolio.allocation."""

import pytest
from trading_system.models.symbol import Symbol
from trading_system.portfolio.allocation import AllocationMethod, PortfolioAllocator


class TestPortfolioAllocatorInit:
    def test_defaults(self) -> None:
        alloc = PortfolioAllocator()
        assert alloc.method == AllocationMethod.EQUAL_WEIGHT
        assert alloc.max_positions == 10

    def test_custom(self) -> None:
        alloc = PortfolioAllocator(
            method=AllocationMethod.RANK_WEIGHTED, max_positions=5, min_weight=0.05
        )
        assert alloc.method == AllocationMethod.RANK_WEIGHTED
        assert alloc.max_positions == 5
        assert alloc.min_weight == 0.05

    def test_invalid_max_positions(self) -> None:
        with pytest.raises(ValueError, match="max_positions must be >= 1"):
            PortfolioAllocator(max_positions=0)

    def test_invalid_min_weight_negative(self) -> None:
        with pytest.raises(ValueError, match="min_weight must be in"):
            PortfolioAllocator(min_weight=-0.1)

    def test_invalid_min_weight_one(self) -> None:
        with pytest.raises(ValueError, match="min_weight must be in"):
            PortfolioAllocator(min_weight=1.0)


class TestPortfolioAllocatorEqualWeight:
    def test_basic(self) -> None:
        alloc = PortfolioAllocator(method=AllocationMethod.EQUAL_WEIGHT, max_positions=3)
        syms = [Symbol(raw="A"), Symbol(raw="B"), Symbol(raw="C")]
        result = alloc.allocate(equity=100000, symbols=syms, scores=[3.0, 2.0, 1.0])
        assert len(result) == 3
        for a in result:
            assert a.weight == pytest.approx(1 / 3)
            assert a.dollar_amount == pytest.approx(100000 / 3)

    def test_trims_to_max_positions(self) -> None:
        alloc = PortfolioAllocator(method=AllocationMethod.EQUAL_WEIGHT, max_positions=2)
        syms = [Symbol(raw="A"), Symbol(raw="B"), Symbol(raw="C")]
        result = alloc.allocate(equity=100000, symbols=syms, scores=[3.0, 2.0, 1.0])
        assert len(result) == 2

    def test_empty_symbols(self) -> None:
        alloc = PortfolioAllocator()
        result = alloc.allocate(equity=100000, symbols=[], scores=[])
        assert result == []


class TestPortfolioAllocatorScoreWeighted:
    def test_proportional_to_scores(self) -> None:
        alloc = PortfolioAllocator(method=AllocationMethod.SCORE_WEIGHTED)
        syms = [Symbol(raw="A"), Symbol(raw="B")]
        result = alloc.allocate(equity=100000, symbols=syms, scores=[3.0, 1.0])
        assert len(result) == 2
        assert result[0].weight == pytest.approx(0.75)
        assert result[1].weight == pytest.approx(0.25)

    def test_equal_scores_equal_weight(self) -> None:
        alloc = PortfolioAllocator(method=AllocationMethod.SCORE_WEIGHTED)
        syms = [Symbol(raw="A"), Symbol(raw="B")]
        result = alloc.allocate(equity=100000, symbols=syms, scores=[2.0, 2.0])
        assert result[0].weight == pytest.approx(0.5)
        assert result[1].weight == pytest.approx(0.5)

    def test_zero_scores_fallback_equal(self) -> None:
        alloc = PortfolioAllocator(method=AllocationMethod.SCORE_WEIGHTED)
        syms = [Symbol(raw="A"), Symbol(raw="B")]
        result = alloc.allocate(equity=100000, symbols=syms, scores=[0.0, 0.0])
        assert result[0].weight == pytest.approx(0.5)

    def test_min_weight_applied(self) -> None:
        alloc = PortfolioAllocator(method=AllocationMethod.SCORE_WEIGHTED, min_weight=0.1)
        syms = [Symbol(raw="A"), Symbol(raw="B")]
        result = alloc.allocate(equity=100000, symbols=syms, scores=[100.0, 1.0])
        assert result[1].weight == pytest.approx(0.1, abs=1e-6)


class TestPortfolioAllocatorRankWeighted:
    def test_top_rank_highest_weight(self) -> None:
        alloc = PortfolioAllocator(method=AllocationMethod.RANK_WEIGHTED)
        syms = [Symbol(raw="A"), Symbol(raw="B"), Symbol(raw="C")]
        result = alloc.allocate(equity=100000, symbols=syms, scores=[1.0, 2.0, 3.0])
        assert result[0].weight > result[1].weight > result[2].weight

    def test_weights_sum_to_one(self) -> None:
        alloc = PortfolioAllocator(method=AllocationMethod.RANK_WEIGHTED)
        syms = [Symbol(raw="A"), Symbol(raw="B"), Symbol(raw="C")]
        result = alloc.allocate(equity=100000, symbols=syms, scores=[1.0, 2.0, 3.0])
        total = sum(a.weight for a in result)
        assert total == pytest.approx(1.0)


class TestPortfolioAllocatorValidation:
    def test_mismatched_lengths(self) -> None:
        alloc = PortfolioAllocator()
        with pytest.raises(ValueError, match="symbols and scores must have same length"):
            alloc.allocate(
                equity=100000,
                symbols=[Symbol(raw="A")],
                scores=[1.0, 2.0],
            )

    def test_zero_equity(self) -> None:
        alloc = PortfolioAllocator()
        with pytest.raises(ValueError, match="equity must be positive"):
            alloc.allocate(equity=0, symbols=[], scores=[])
