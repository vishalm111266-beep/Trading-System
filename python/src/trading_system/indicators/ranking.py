"""Stock ranking by relative strength metrics."""

from __future__ import annotations

from trading_system.indicators.normalization import zscore
from trading_system.models.ranking_result import RankedSymbol, RankingResult
from trading_system.models.symbol import Symbol


def rank_by_rs(
    symbols: list[Symbol],
    scores: list[float],
) -> RankingResult:
    """Rank symbols by score in descending order.

    *symbols* and *scores* must have the same length.
    """
    if len(symbols) != len(scores):
        msg = f"length mismatch: symbols={len(symbols)}, scores={len(scores)}"
        raise ValueError(msg)
    if not symbols:
        return RankingResult()

    paired = sorted(
        zip(symbols, scores, strict=True), key=lambda p: p[1], reverse=True
    )
    entries = tuple(
        RankedSymbol(symbol=sym, rank=i + 1, score=sc)
        for i, (sym, sc) in enumerate(paired)
    )
    return RankingResult(entries=entries)


def rank_by_zscore(
    symbols: list[Symbol],
    values: list[float],
) -> RankingResult:
    """Normalize values to Z-scores then rank descending."""
    scores = zscore(values)
    float_scores = [s if s is not None else 0.0 for s in scores]
    return rank_by_rs(symbols, float_scores)
