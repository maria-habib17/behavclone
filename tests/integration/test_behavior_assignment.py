from pathlib import Path

import pytest

from behavclone.behavior.assignment import (
    behavioral_results_path,
    compare_assignment_behavior,
    load_assignment_behavior,
)
from behavclone.ingestion.assignment import load_assignment

DEMO_ASSIGNMENT = (
    Path(__file__).parents[2]
    / "datasets"
    / "synthetic"
    / "demo-assignment"
)


def test_resolves_configured_behavioral_results_path():
    assignment = load_assignment(DEMO_ASSIGNMENT)

    path = behavioral_results_path(assignment)

    assert path == assignment.root / "test-results.csv"


def test_loads_demo_assignment_behavioral_results():
    assignment = load_assignment(DEMO_ASSIGNMENT)

    dataset = load_assignment_behavior(assignment)

    assert dataset.submission_ids == frozenset({
        "S001",
        "S002",
    })
    assert dataset.test_ids == frozenset({
        "T01",
        "T02",
        "T03",
    })
    assert len(dataset.observations) == 6


def test_shared_correct_behavior_is_not_reported_as_evidence():
    assignment = load_assignment(DEMO_ASSIGNMENT)

    evidence = compare_assignment_behavior(
        assignment,
        "S001",
        "S002",
    )

    assert [
        item.test_id
        for item in evidence.shared_failures
    ] == ["T03"]

    assert "T01" not in {
        item.test_id
        for item in evidence.shared_failures
    }
    assert "T02" not in {
        item.test_id
        for item in evidence.shared_failures
    }


def test_demo_pair_surfaces_identical_wrong_output():
    assignment = load_assignment(DEMO_ASSIGNMENT)

    evidence = compare_assignment_behavior(
        assignment,
        "S001",
        "S002",
    )

    assert evidence.shared_failure_count == 1
    assert evidence.identical_wrong_output_count == 1

    shared = evidence.shared_failures[0]

    assert shared.test_id == "T03"
    assert shared.expected == "100"
    assert shared.left_actual == "99"
    assert shared.right_actual == "99"
    assert shared.identical_wrong_output


def test_demo_pair_reports_behavioral_cohort_frequency():
    assignment = load_assignment(DEMO_ASSIGNMENT)

    evidence = compare_assignment_behavior(
        assignment,
        "S001",
        "S002",
    )

    shared = evidence.shared_failures[0]

    assert evidence.cohort_size == 2
    assert shared.failure_count == 2
    assert shared.wrong_output_count == 2
    assert shared.failure_proportion == pytest.approx(1.0)
    assert shared.wrong_output_proportion == pytest.approx(1.0)


def test_assignment_without_test_results_is_rejected(
    tmp_path: Path,
):
    assignment_root = tmp_path / "assignment"
    submissions = assignment_root / "submissions"
    submissions.mkdir(parents=True)

    (submissions / "S001").mkdir()

    (assignment_root / "assignment.yaml").write_text(
        (
            "assignment:\n"
            "  name: no-behavior\n"
            "  language: java\n"
            "  submissions_directory: submissions\n"
            "  test_results: null\n"
        ),
        encoding="utf-8",
    )

    assignment = load_assignment(assignment_root)

    assert behavioral_results_path(assignment) is None

    with pytest.raises(
        ValueError,
        match="does not configure behavioral test results",
    ):
        load_assignment_behavior(assignment)


def test_missing_configured_results_file_is_rejected(
    tmp_path: Path,
):
    assignment_root = tmp_path / "assignment"
    submissions = assignment_root / "submissions"
    submissions.mkdir(parents=True)

    (submissions / "S001").mkdir()

    (assignment_root / "assignment.yaml").write_text(
        (
            "assignment:\n"
            "  name: missing-results\n"
            "  language: java\n"
            "  submissions_directory: submissions\n"
            "  test_results: missing.csv\n"
        ),
        encoding="utf-8",
    )

    assignment = load_assignment(assignment_root)

    with pytest.raises(
        FileNotFoundError,
        match="Behavioral results file does not exist",
    ):
        load_assignment_behavior(assignment)


def test_unknown_assignment_submission_is_rejected():
    assignment = load_assignment(DEMO_ASSIGNMENT)

    with pytest.raises(
        ValueError,
        match="Unknown assignment submission: S999",
    ):
        compare_assignment_behavior(
            assignment,
            "S999",
            "S001",
        )
