from pathlib import Path

from behavclone.ingestion.assignment import load_assignment
from experiments.synthetic import (
    controlled_submissions,
    write_synthetic_assignment,
)


def test_controlled_submission_ids_are_unique():
    submissions = controlled_submissions()

    submission_ids = [
        submission.submission_id
        for submission in submissions
    ]

    assert len(submission_ids) == len(
        set(submission_ids)
    )


def test_synthetic_assignment_is_loadable(
    tmp_path: Path,
):
    root = tmp_path / "assignment"

    write_synthetic_assignment(
        root,
        controlled_submissions(),
    )

    assignment = load_assignment(root)

    assert {
        submission.submission_id
        for submission in assignment.submissions
    } == {
        "BASE",
        "ID_RENAME",
        "METHOD_REORDER",
        "CLASS_RENAME",
        "FILE_RENAME",
        "DEAD_CODE",
        "CLASS_SPLIT",
        "UNRELATED_A",
        "UNRELATED_B",
        "LOOKALIKE",
    }


def test_every_controlled_submission_contains_java_source():
    submissions = controlled_submissions()

    for submission in submissions:
        assert submission.files
        assert all(
            path.endswith(".java")
            for path in submission.files
        )


def test_class_split_uses_multiple_source_files():
    submissions = {
        submission.submission_id: submission
        for submission in controlled_submissions()
    }

    class_split = submissions["CLASS_SPLIT"]

    assert set(class_split.files) == {
        "Incrementer.java",
        "Multiplier.java",
    }
