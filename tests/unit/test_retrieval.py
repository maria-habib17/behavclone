import pytest

from experiments.evaluation import rank_benchmark
from experiments.models import (
    BenchmarkResult,
    PairMetrics,
    TransformationKind,
)
from experiments.retrieval import (
    average_precision,
    evaluate_retrieval,
    precision_at_k,
    recall_at_k,
)


def pair(
    right: str,
    score: float,
    related: bool,
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
        matched_count=1,
        left_coverage=1.0,
        right_coverage=1.0,
        mean_raw_similarity=score,
        mean_normalized_similarity=score,
        mean_structural_similarity=score,
    )


def mixed_result() -> BenchmarkResult:
    return BenchmarkResult(
        pairs=(
            pair("POS_A", 0.95, True),
            pair("NEG_A", 0.90, False),
            pair("POS_B", 0.80, True),
            pair("NEG_B", 0.70, False),
        )
    )


def test_precision_and_recall_at_k():
    ranking = rank_benchmark(
        mixed_result(),
        "normalized",
    )

    assert precision_at_k(
        ranking,
        1,
    ) == pytest.approx(1.0)

    assert precision_at_k(
        ranking,
        2,
    ) == pytest.approx(0.5)

    assert recall_at_k(
        ranking,
        1,
    ) == pytest.approx(0.5)

    assert recall_at_k(
        ranking,
        3,
    ) == pytest.approx(1.0)


def test_average_precision_uses_positive_ranks():
    ranking = rank_benchmark(
        mixed_result(),
        "normalized",
    )

    expected = (
        1.0
        + (2 / 3)
    ) / 2

    assert average_precision(
        ranking
    ) == pytest.approx(expected)


def test_evaluate_retrieval_reports_requested_k_values():
    metrics = evaluate_retrieval(
        mixed_result(),
        "normalized",
        k_values=(3, 1, 2),
    )

    assert metrics.pair_count == 4
    assert metrics.related_count == 2

    assert tuple(
        metrics.precision_at_k
    ) == (1, 2, 3)

    assert tuple(
        metrics.recall_at_k
    ) == (1, 2, 3)

    assert metrics.first_unrelated_rank == 2


def test_k_larger_than_pair_count_uses_available_pairs():
    ranking = rank_benchmark(
        mixed_result(),
        "normalized",
    )

    assert precision_at_k(
        ranking,
        100,
    ) == pytest.approx(0.5)

    assert recall_at_k(
        ranking,
        100,
    ) == pytest.approx(1.0)


def test_no_positive_pairs_have_undefined_average_precision():
    result = BenchmarkResult(
        pairs=(
            pair("NEG_A", 0.9, False),
            pair("NEG_B", 0.8, False),
        )
    )

    ranking = rank_benchmark(
        result,
        "normalized",
    )

    assert average_precision(
        ranking
    ) is None

    metrics = evaluate_retrieval(
        result,
        "normalized",
        k_values=(1,),
    )

    assert metrics.related_count == 0
    assert metrics.recall_at_k[1] == 0.0


@pytest.mark.parametrize(
    "k_values",
    [
        (),
        (0,),
        (-1,),
        (1, 1),
    ],
)
def test_invalid_k_values_are_rejected(
    k_values,
):
    with pytest.raises(ValueError):
        evaluate_retrieval(
            mixed_result(),
            "normalized",
            k_values=k_values,
        )
