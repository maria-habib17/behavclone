from pathlib import Path

from behavclone.ingestion.assignment import (
    discover_java_files,
    load_assignment,
)

DEMO = Path("datasets/synthetic/demo-assignment")


def test_assignment_loads():
    assignment = load_assignment(DEMO)

    assert assignment.config.name == "Synthetic OOP Assignment"
    assert assignment.config.language == "java"


def test_two_submissions_are_discovered():
    assignment = load_assignment(DEMO)

    assert len(assignment.submissions) == 2

    ids = {
        submission.submission_id
        for submission in assignment.submissions
    }

    assert ids == {"S001", "S002"}


def test_java_files_are_discovered_recursively():
    assignment = load_assignment(DEMO)

    assert all(
        len(submission.source_files) == 1
        for submission in assignment.submissions
    )


def test_different_filenames_are_supported():
    assignment = load_assignment(DEMO)

    filenames = {
        file.name
        for submission in assignment.submissions
        for file in submission.source_files
    }

    assert filenames == {
        "Calculator.java",
        "PricingEngine.java",
    }


def test_java_discovery_ignores_non_java_files(tmp_path):
    java_file = tmp_path / "Example.java"
    text_file = tmp_path / "notes.txt"

    java_file.write_text(
        "class Example {}",
        encoding="utf-8",
    )

    text_file.write_text(
        "ignore me",
        encoding="utf-8",
    )

    result = discover_java_files(tmp_path)

    assert result == [java_file]
