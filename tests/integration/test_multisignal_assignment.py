from pathlib import Path

import pytest

from behavclone.evidence.assignment import (
    compare_assignment_pair_evidence,
)
from behavclone.ingestion.assignment import load_assignment

DEMO_ASSIGNMENT = (
    Path(__file__).parents[2]
    / "datasets"
    / "synthetic"
    / "demo-assignment"
)


def test_pair_evidence_exposes_three_separate_channels():
    assignment = load_assignment(DEMO_ASSIGNMENT)

    evidence = compare_assignment_pair_evidence(
        assignment,
        "S001",
        "S002",
        ngram_size=4,
    )

    assert evidence.left_submission_id == "S001"
    assert evidence.right_submission_id == "S002"

    assert evidence.structural.matched_count > 0
    assert evidence.cohort.shared_feature_count > 0

    assert evidence.behavioral is not None
    assert evidence.behavioral.shared_failure_count == 1
    assert evidence.behavioral.identical_wrong_output_count == 1


def test_pair_evidence_preserves_structural_similarity_measurements():
    assignment = load_assignment(DEMO_ASSIGNMENT)

    evidence = compare_assignment_pair_evidence(
        assignment,
        "S001",
        "S002",
    )

    assert 0.0 <= evidence.structural.mean_raw_similarity <= 1.0
    assert (
        0.0
        <= evidence.structural.mean_normalized_similarity
        <= 1.0
    )
    assert (
        0.0
        <= evidence.structural.mean_structural_similarity
        <= 1.0
    )


def test_pair_evidence_preserves_cohort_context():
    assignment = load_assignment(DEMO_ASSIGNMENT)

    evidence = compare_assignment_pair_evidence(
        assignment,
        "S001",
        "S002",
        ngram_size=4,
    )

    assert evidence.cohort.cohort_size == 2
    assert evidence.cohort.ngram_size == 4
    assert evidence.cohort.max_rarity >= 1.0


def test_pair_evidence_preserves_behavioral_wrong_output_rarity():
    assignment = load_assignment(DEMO_ASSIGNMENT)

    evidence = compare_assignment_pair_evidence(
        assignment,
        "S001",
        "S002",
    )

    assert evidence.behavioral is not None
    assert evidence.behavioral.max_failure_rarity >= 1.0
    assert evidence.behavioral.max_wrong_output_rarity >= 1.0


def test_pair_without_configured_behavior_keeps_channel_absent(
    tmp_path: Path,
):
    submissions = tmp_path / "submissions"
    left = submissions / "S001"
    right = submissions / "S002"

    left.mkdir(parents=True)
    right.mkdir(parents=True)

    (tmp_path / "assignment.yaml").write_text(
        (
            "assignment:\n"
            "  name: no-behavior\n"
            "  language: java\n"
            "  submissions_directory: submissions\n"
            "  starter_directory: null\n"
            "  test_results: null\n"
        ),
        encoding="utf-8",
    )

    (left / "First.java").write_text(
        (
            "class First {\n"
            "    int calculate(int value) {\n"
            "        return value + 1;\n"
            "    }\n"
            "}\n"
        ),
        encoding="utf-8",
    )

    (right / "Second.java").write_text(
        (
            "class Second {\n"
            "    int compute(int number) {\n"
            "        return number + 1;\n"
            "    }\n"
            "}\n"
        ),
        encoding="utf-8",
    )

    assignment = load_assignment(tmp_path)

    evidence = compare_assignment_pair_evidence(
        assignment,
        "S001",
        "S002",
    )

    assert evidence.structural.matched_count == 1
    assert evidence.cohort.shared_feature_count > 0
    assert evidence.behavioral is None


def test_pair_evidence_rejects_unknown_submission():
    assignment = load_assignment(DEMO_ASSIGNMENT)

    with pytest.raises(
        ValueError,
        match="Unknown assignment submission: UNKNOWN",
    ):
        compare_assignment_pair_evidence(
            assignment,
            "S001",
            "UNKNOWN",
        )
