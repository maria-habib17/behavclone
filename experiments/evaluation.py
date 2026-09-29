from dataclasses import dataclass
from typing import Literal

from experiments.models import (
    BenchmarkResult,
    PairMetrics,
)

SimilarityMetric = Literal[
    "raw",
    "normalized",
    "structural",
]


@dataclass(frozen=True)
class RankedPair:
    """One benchmark pair together with its rank."""

    pair: PairMetrics
    rank: int
    score: float


@dataclass(frozen=True)
class RankingEvaluation:
    """Ranking measurements for one similarity representation."""

    metric: SimilarityMetric
    ranked_pairs: tuple[RankedPair, ...]

    @property
    def related_ranks(self) -> tuple[int, ...]:
        return tuple(
            item.rank
            for item in self.ranked_pairs
            if item.pair.related
        )

    @property
    def unrelated_ranks(self) -> tuple[int, ...]:
        return tuple(
            item.rank
            for item in self.ranked_pairs
            if not item.pair.related
        )

    @property
    def mean_related_rank(self) -> float | None:
        ranks = self.related_ranks

        if not ranks:
            return None

        return sum(ranks) / len(ranks)

    @property
    def best_unrelated_rank(self) -> int | None:
        ranks = self.unrelated_ranks

        if not ranks:
            return None

        return min(ranks)


def _score(
    pair: PairMetrics,
    metric: SimilarityMetric,
) -> float:
    if metric == "raw":
        return pair.mean_raw_similarity

    if metric == "normalized":
        return pair.mean_normalized_similarity

    if metric == "structural":
        return pair.mean_structural_similarity

    raise ValueError(
        f"Unsupported similarity metric: {metric}"
    )


def rank_benchmark(
    result: BenchmarkResult,
    metric: SimilarityMetric,
) -> RankingEvaluation:
    """Rank benchmark pairs by one explicitly selected similarity metric."""
    scored = [
        (pair, _score(pair, metric))
        for pair in result.pairs
    ]

    scored.sort(
        key=lambda item: (
            -item[1],
            item[0].right_submission_id,
            item[0].left_submission_id,
        )
    )

    ranked = tuple(
        RankedPair(
            pair=pair,
            rank=index,
            score=score,
        )
        for index, (pair, score) in enumerate(
            scored,
            start=1,
        )
    )

    return RankingEvaluation(
        metric=metric,
        ranked_pairs=ranked,
    )
