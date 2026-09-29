from pathlib import Path

import pytest

from behavclone.ingestion.assignment import load_assignment
from experiments.controlled import controlled_pairs
from experiments.models import (
    BenchmarkPair,
    TransformationKind,
)
from experiments.runner import run_structural_benchmark
from experiments.synthetic import (
    controlled_submissions,
    write_synthetic_assignment,
)


def write_assignment(root: Path) -> None:
    (root / "submissions" / "S001").mkdir(
        parents=True
    )
    (root / "submissions" / "S002").mkdir(
        parents=True
    )

    (root / "assignment.yaml").write_text(
        (
            "assignment:\n"
            "  name: transformation-benchmark\n"
            "  language: java\n"
            "  submissions_directory: submissions\n"
            "  starter_directory: null\n"
        ),
        encoding="utf-8",
    )

    (
        root
        / "submissions"
        / "S001"
        / "Calculator.java"
    ).write_text(
        """
class Calculator {
    int increase(int value) {
        int result = value + 1;
        return result;
    }

    int multiply(int value) {
        int result = value * 17;
        return result;
    }
}
""".strip(),
        encoding="utf-8",
    )

    (
        root
        / "submissions"
        / "S002"
        / "PricingEngine.java"
    ).write_text(
        """
class PricingEngine {
    int scale(int input) {
        int changed = input * 17;
        return changed;
    }

    int raise(int input) {
        int changed = input + 1;
        return changed;
    }
}
""".strip(),
        encoding="utf-8",
    )


def test_benchmark_survives_identifier_and_method_reordering(
    tmp_path: Path,
):
    root = tmp_path / "assignment"
    write_assignment(root)

    assignment = load_assignment(root)

    result = run_structural_benchmark(
        assignment,
        (
            BenchmarkPair(
                left_submission_id="S001",
                right_submission_id="S002",
                related=True,
                transformation=(
                    TransformationKind.METHOD_REORDER
                ),
            ),
        ),
    )

    pair = result.pairs[0]

    assert pair.matched_count == 2
    assert pair.left_coverage == pytest.approx(1.0)
    assert pair.right_coverage == pytest.approx(1.0)
    assert pair.mean_normalized_similarity == pytest.approx(
        1.0
    )
    assert pair.mean_structural_similarity == pytest.approx(
        1.0
    )


def test_benchmark_records_default_assignment_metric(
    tmp_path: Path,
):
    root = tmp_path / "assignment"

    write_synthetic_assignment(
        root,
        controlled_submissions(),
    )

    assignment = load_assignment(root)

    result = run_structural_benchmark(
        assignment,
        controlled_pairs(),
    )

    assert result.assignment_metric == "normalized"


def test_benchmark_records_requested_assignment_metric(
    tmp_path: Path,
):
    root = tmp_path / "assignment"

    write_synthetic_assignment(
        root,
        controlled_submissions(),
    )

    assignment = load_assignment(root)

    for metric in (
        "raw",
        "normalized",
        "structural",
    ):
        result = run_structural_benchmark(
            assignment,
            controlled_pairs(),
            assignment_metric=metric,
        )

        assert result.assignment_metric == metric
