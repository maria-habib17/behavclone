import pytest

from experiments.evaluation import rank_benchmark
from experiments.models import (
    BenchmarkResult,
    PairMetrics,
    TransformationKind,
)


def pair(
    right: str,
    related: bool,
    normalized: float,
    structural: float,
) -> PairMetrics:
    return PairMetrics(
        left_submission_id="BASE",
        right_submission_id=right,
        related=related,
        transformation=(
            TransformationKind.IDENTIFIER_RENAME
            if related
            else None
        ),
        matched_count=2,
        left_coverage=1.0,
        right_coverage=1.0,
        mean_raw_similarity=0.5,
        mean_normalized_similarity=normalized,
        mean_structural_similarity=structural,
    )


def test_normalized_ranking_orders_highest_score_first():
    result = BenchmarkResult(
        pairs=(
            pair("RELATED", True, 0.95, 0.70),
            pair("CONTROL_A", False, 0.40, 0.90),
            pair("CONTROL_B", False, 0.20, 0.30),
        )
    )

    evaluation = rank_benchmark(
        result,
        "normalized",
    )

    assert [
        item.pair.right_submission_id
        for item in evaluation.ranked_pairs
    ] == [
        "RELATED",
        "CONTROL_A",
        "CONTROL_B",
    ]

    assert evaluation.related_ranks == (1,)
    assert evaluation.best_unrelated_rank == 2


def test_structural_ranking_is_independent():
    result = BenchmarkResult(
        pairs=(
            pair("RELATED", True, 0.95, 0.70),
            pair("CONTROL", False, 0.40, 0.90),
        )
    )

    evaluation = rank_benchmark(
        result,
        "structural",
    )

    assert (
        evaluation.ranked_pairs[0].pair.right_submission_id
        == "CONTROL"
    )
    assert evaluation.related_ranks == (2,)
    assert evaluation.best_unrelated_rank == 1


def test_mean_related_rank_is_reported():
    result = BenchmarkResult(
        pairs=(
            pair("RELATED_A", True, 0.90, 0.90),
            pair("CONTROL", False, 0.80, 0.80),
            pair("RELATED_B", True, 0.70, 0.70),
        )
    )

    evaluation = rank_benchmark(
        result,
        "normalized",
    )

    assert evaluation.related_ranks == (1, 3)
    assert evaluation.mean_related_rank == pytest.approx(2.0)


def test_ties_are_deterministic():
    result = BenchmarkResult(
        pairs=(
            pair("ZETA", False, 0.50, 0.50),
            pair("ALPHA", False, 0.50, 0.50),
        )
    )

    evaluation = rank_benchmark(
        result,
        "normalized",
    )

    assert [
        item.pair.right_submission_id
        for item in evaluation.ranked_pairs
    ] == [
        "ALPHA",
        "ZETA",
    ]


def test_empty_result_has_no_summary_ranks():
    evaluation = rank_benchmark(
        BenchmarkResult(pairs=()),
        "normalized",
    )

    assert evaluation.ranked_pairs == ()
    assert evaluation.related_ranks == ()
    assert evaluation.unrelated_ranks == ()
    assert evaluation.mean_related_rank is None
    assert evaluation.best_unrelated_rank is None


def test_unsupported_metric_is_rejected():
    result = BenchmarkResult(
        pairs=(
            pair("CONTROL", False, 0.5, 0.5),
        )
    )

    with pytest.raises(
        ValueError,
        match="Unsupported similarity metric",
    ):
        rank_benchmark(
            result,
            "unsupported",  # type: ignore[arg-type]
        )


def test_raw_ranking_uses_raw_similarity():
    result = BenchmarkResult(
        pairs=(
            PairMetrics(
                left_submission_id="BASE",
                right_submission_id="RELATED",
                related=True,
                transformation=(
                    TransformationKind.IDENTIFIER_RENAME
                ),
                matched_count=2,
                left_coverage=1.0,
                right_coverage=1.0,
                mean_raw_similarity=0.4,
                mean_normalized_similarity=1.0,
                mean_structural_similarity=1.0,
            ),
            PairMetrics(
                left_submission_id="BASE",
                right_submission_id="CONTROL",
                related=False,
                transformation=None,
                matched_count=2,
                left_coverage=1.0,
                right_coverage=1.0,
                mean_raw_similarity=0.8,
                mean_normalized_similarity=0.5,
                mean_structural_similarity=0.5,
            ),
        )
    )

    evaluation = rank_benchmark(
        result,
        "raw",
    )

    assert evaluation.metric == "raw"
    assert (
        evaluation.ranked_pairs[0].pair.right_submission_id
        == "CONTROL"
    )
    assert evaluation.ranked_pairs[0].score == pytest.approx(
        0.8
    )
