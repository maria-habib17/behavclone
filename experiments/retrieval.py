"""Retrieval-oriented evaluation for labeled similarity pairs."""

from dataclasses import dataclass

from experiments.evaluation import (
    RankingEvaluation,
    SimilarityMetric,
    rank_benchmark,
)
from experiments.models import BenchmarkResult


@dataclass(frozen=True)
class RetrievalMetrics:
    """Retrieval measurements for one ranked benchmark."""

    metric: SimilarityMetric
    pair_count: int
    related_count: int
    precision_at_k: dict[int, float]
    recall_at_k: dict[int, float]
    average_precision: float | None
    first_unrelated_rank: int | None


def _validate_k_values(
    k_values: tuple[int, ...],
) -> tuple[int, ...]:
    if not k_values:
        raise ValueError(
            "At least one K value is required."
        )

    if any(k <= 0 for k in k_values):
        raise ValueError(
            "K values must be positive."
        )

    if len(set(k_values)) != len(k_values):
        raise ValueError(
            "K values must be unique."
        )

    return tuple(sorted(k_values))


def precision_at_k(
    ranking: RankingEvaluation,
    k: int,
) -> float:
    """Return precision among the first min(K, pair_count) pairs."""
    if k <= 0:
        raise ValueError(
            "K must be positive."
        )

    selected = ranking.ranked_pairs[:k]

    if not selected:
        return 0.0

    related = sum(
        item.pair.related
        for item in selected
    )

    return related / len(selected)


def recall_at_k(
    ranking: RankingEvaluation,
    k: int,
) -> float:
    """Return fraction of all labeled positives retrieved by K."""
    if k <= 0:
        raise ValueError(
            "K must be positive."
        )

    total_related = len(
        ranking.related_ranks
    )

    if total_related == 0:
        return 0.0

    retrieved = sum(
        item.pair.related
        for item in ranking.ranked_pairs[:k]
    )

    return retrieved / total_related


def average_precision(
    ranking: RankingEvaluation,
) -> float | None:
    """Return average precision across positive retrieval ranks."""
    total_related = len(
        ranking.related_ranks
    )

    if total_related == 0:
        return None

    precision_sum = 0.0
    related_seen = 0

    for index, item in enumerate(
        ranking.ranked_pairs,
        start=1,
    ):
        if not item.pair.related:
            continue

        related_seen += 1
        precision_sum += related_seen / index

    return precision_sum / total_related


def evaluate_retrieval(
    result: BenchmarkResult,
    metric: SimilarityMetric,
    k_values: tuple[int, ...] = (5, 10, 20),
) -> RetrievalMetrics:
    """Evaluate labeled-pair retrieval for one similarity metric."""
    validated_k = _validate_k_values(
        k_values
    )

    ranking = rank_benchmark(
        result,
        metric,
    )

    return RetrievalMetrics(
        metric=metric,
        pair_count=len(ranking.ranked_pairs),
        related_count=len(ranking.related_ranks),
        precision_at_k={
            k: precision_at_k(ranking, k)
            for k in validated_k
        },
        recall_at_k={
            k: recall_at_k(ranking, k)
            for k in validated_k
        },
        average_precision=average_precision(
            ranking
        ),
        first_unrelated_rank=(
            ranking.best_unrelated_rank
        ),
    )
