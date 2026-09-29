import pytest

from experiments.models import (
    BenchmarkPair,
    BenchmarkResult,
    PairMetrics,
    TransformationKind,
)


def test_related_pair_requires_transformation():
    with pytest.raises(
        ValueError,
        match="require a transformation",
    ):
        BenchmarkPair(
            left_submission_id="S001",
            right_submission_id="S002",
            related=True,
        )


def test_unrelated_pair_cannot_have_transformation():
    with pytest.raises(
        ValueError,
        match="cannot declare a transformation",
    ):
        BenchmarkPair(
            left_submission_id="S001",
            right_submission_id="S002",
            related=False,
            transformation=(
                TransformationKind.IDENTIFIER_RENAME
            ),
        )


def test_benchmark_result_separates_pair_labels():
    related = PairMetrics(
        left_submission_id="S001",
        right_submission_id="S002",
        related=True,
        transformation=TransformationKind.METHOD_REORDER,
        matched_count=2,
        left_coverage=1.0,
        right_coverage=1.0,
        mean_raw_similarity=0.5,
        mean_normalized_similarity=1.0,
        mean_structural_similarity=1.0,
    )

    unrelated = PairMetrics(
        left_submission_id="S001",
        right_submission_id="S003",
        related=False,
        transformation=None,
        matched_count=1,
        left_coverage=0.5,
        right_coverage=0.5,
        mean_raw_similarity=0.5,
        mean_normalized_similarity=0.4,
        mean_structural_similarity=0.5,
    )

    result = BenchmarkResult(
        pairs=(related, unrelated)
    )

    assert result.related_pairs == (related,)
    assert result.unrelated_pairs == (unrelated,)
