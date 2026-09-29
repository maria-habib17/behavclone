from collections.abc import Iterable

from behavclone.fragments.starter import build_starter_signatures
from behavclone.ingestion.models import Assignment
from behavclone.matching.models import MatchingMetric
from behavclone.matching.submission import compare_submissions
from experiments.models import (
    BenchmarkPair,
    BenchmarkResult,
    PairMetrics,
)


def _submission_files(
    assignment: Assignment,
) -> dict[str, list]:
    return {
        submission.submission_id: submission.source_files
        for submission in assignment.submissions
    }


def run_structural_benchmark(
    assignment: Assignment,
    pairs: Iterable[BenchmarkPair],
    assignment_metric: MatchingMetric = "normalized",
) -> BenchmarkResult:
    """Measure labeled pairs using metric-selected correspondence."""
    source_files = _submission_files(assignment)
    starter_signatures = build_starter_signatures(
        assignment.starter_files
    )

    results: list[PairMetrics] = []

    for pair in pairs:
        if pair.left_submission_id not in source_files:
            raise ValueError(
                "Unknown benchmark submission: "
                f"{pair.left_submission_id}"
            )

        if pair.right_submission_id not in source_files:
            raise ValueError(
                "Unknown benchmark submission: "
                f"{pair.right_submission_id}"
            )

        comparison = compare_submissions(
            source_files[pair.left_submission_id],
            source_files[pair.right_submission_id],
            starter_signatures=starter_signatures,
            metric=assignment_metric,
        )

        results.append(
            PairMetrics(
                left_submission_id=pair.left_submission_id,
                right_submission_id=pair.right_submission_id,
                related=pair.related,
                transformation=pair.transformation,
                matched_count=comparison.matched_count,
                left_coverage=comparison.left_coverage,
                right_coverage=comparison.right_coverage,
                mean_raw_similarity=comparison.mean_raw_similarity,
                mean_normalized_similarity=(
                    comparison.mean_normalized_similarity
                ),
                mean_structural_similarity=(
                    comparison.mean_structural_similarity
                ),
            )
        )

    return BenchmarkResult(
        pairs=tuple(results),
        assignment_metric=assignment_metric,
    )
